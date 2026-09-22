#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
COMPOSE=(docker compose -f docker-compose.dev.yml)
FIXTURE=/tmp/unividown-phase3b.mp4
STATUS_JSON=/tmp/unividown-phase3b-status.json
RESULT_FILE=/tmp/unividown-phase3b-result.webm
INVALID_JSON=/tmp/unividown-phase3b-invalid.json
LOG_FILE="$ROOT/phase3b-compose.log"

cleanup() {
  "${COMPOSE[@]}" logs --no-color worker web redis >"$LOG_FILE" 2>&1 || true
  "${COMPOSE[@]}" down -v >/dev/null 2>&1 || true
  rm -f "$FIXTURE" "$STATUS_JSON" "$RESULT_FILE" "$INVALID_JSON"
}
trap cleanup EXIT

for command in pnpm python3 docker curl ffmpeg ffprobe; do
  command -v "$command" >/dev/null || { echo "ERROR: missing command: $command"; exit 1; }
done

echo "[1/8] Frontend install, lint, typecheck, build"
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm build

echo "[2/8] Backend dependencies and tests"
services/worker/.venv/bin/pip install -r services/worker/requirements.txt
(
  cd services/worker
  .venv/bin/pytest -v
)

echo "[3/8] Build and start development Compose"
"${COMPOSE[@]}" down -v
"${COMPOSE[@]}" config --quiet
"${COMPOSE[@]}" up -d --build --wait
"${COMPOSE[@]}" ps

echo "[4/8] Generate fixture and queue conversion"
ffmpeg -loglevel error \
  -f lavfi -i color=c=blue:s=320x240:d=3 \
  -f lavfi -i sine=frequency=440:duration=3 \
  -c:v libx264 -c:a aac -shortest -y "$FIXTURE"

mapfile -t BEFORE_UPLOADS < <("${COMPOSE[@]}" exec -T worker sh -lc 'find /app/data/uploads -maxdepth 1 -type f -printf "%f\n" | sort')
RESPONSE="$(curl -fsS -F "file=@${FIXTURE};filename=phase3b.mp4" -F 'format=webm' http://localhost:8000/api/tools/convert)"
JOB_ID="$(printf '%s' "$RESPONSE" | python3 -c 'import json,sys; print(json.load(sys.stdin)["job_id"])')"
STATUS_URL="$(printf '%s' "$RESPONSE" | python3 -c 'import json,sys; print(json.load(sys.stdin)["status_url"])')"
echo "Queued job $JOB_ID"

echo "[5/8] Poll status"
STATUS="pending"
for attempt in $(seq 1 60); do
  curl -fsS "http://localhost:8000${STATUS_URL}" -o "$STATUS_JSON"
  STATUS="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$STATUS_JSON")"
  echo "attempt=$attempt status=$STATUS"
  [[ "$STATUS" == "completed" || "$STATUS" == "failed" ]] && break
  sleep 2
done
python3 -m json.tool "$STATUS_JSON"
[[ "$STATUS" == "completed" ]] || { echo "ERROR: processing ended with status=$STATUS"; exit 1; }
if grep -Eq '"input_files"|"output_files"|/app/data|data/uploads|data/processed' "$STATUS_JSON"; then
  echo "ERROR: filesystem path leaked in status response"
  exit 1
fi

echo "[6/8] Download and inspect result"
RESULT_URL="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["results"][0]["download_url"])' "$STATUS_JSON")"
curl -fSL "http://localhost:8000${RESULT_URL}" -o "$RESULT_FILE"
test -s "$RESULT_FILE"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 "$RESULT_FILE"
HTTP_CODE="$(curl -sS -o "$INVALID_JSON" -w '%{http_code}' "http://localhost:8000/api/tools/jobs/${JOB_ID}/files/999")"
[[ "$HTTP_CODE" == "404" ]] || { echo "ERROR: invalid result index returned HTTP $HTTP_CODE"; exit 1; }

mapfile -t AFTER_UPLOADS < <("${COMPOSE[@]}" exec -T worker sh -lc 'find /app/data/uploads -maxdepth 1 -type f -printf "%f\n" | sort')
[[ "${BEFORE_UPLOADS[*]}" == "${AFTER_UPLOADS[*]}" ]] || { echo "ERROR: terminal job left an upload input behind"; exit 1; }
! "${COMPOSE[@]}" exec -T worker sh -lc 'find /app/data/uploads -maxdepth 1 -name "*.part" -print -quit' | grep -q . || { echo "ERROR: partial upload remains"; exit 1; }

echo "[7/8] Restart recovery"
"${COMPOSE[@]}" stop worker
RECOVERY_JOB_ID="$(python3 - <<'PY'
import json, sqlite3
connection = sqlite3.connect('data/unividown.db')
cursor = connection.execute(
    '''INSERT INTO processing_jobs
       (tool_type, status, progress, input_files, output_files, parameters)
       VALUES (?, ?, ?, ?, ?, ?)''',
    ('convert', 'processing', 25.0, json.dumps(['/app/data/uploads/missing-recovery.mp4']), None, json.dumps({'format': 'mp4'})),
)
connection.commit()
print(cursor.lastrowid)
connection.close()
PY
)"
"${COMPOSE[@]}" start worker
sleep 6
RECOVERY_STATUS="$(python3 - "$RECOVERY_JOB_ID" <<'PY'
import sqlite3, sys
connection = sqlite3.connect('data/unividown.db')
row = connection.execute('SELECT status FROM processing_jobs WHERE id = ?', (int(sys.argv[1]),)).fetchone()
connection.close()
print(row[0])
PY
)"
[[ "$RECOVERY_STATUS" != "processing" ]] || { echo "ERROR: recovered job is still processing"; exit 1; }
"${COMPOSE[@]}" logs --no-color worker | grep -Ei 'Recovered .*interrupted processing job' >/dev/null || { echo "ERROR: recovery log not found"; exit 1; }

echo "[8/8] PASS"
echo "Phase 3B validation passed. Logs: $LOG_FILE"
