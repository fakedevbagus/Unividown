#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
COMPOSE="docker compose -f docker-compose.dev.yml"
FIXTURE=/tmp/unividown-phase3b.mp4
STATUS_JSON=/tmp/unividown-phase3b-status.json
RESULT_FILE=/tmp/unividown-phase3b-result.webm
LOG_FILE="$ROOT/phase3b-compose.log"

cleanup() {
  $COMPOSE logs --no-color worker web redis >"$LOG_FILE" 2>&1 || true
  $COMPOSE down -v >/dev/null 2>&1 || true
  rm -f "$FIXTURE" "$STATUS_JSON" "$RESULT_FILE"
}
trap cleanup EXIT

for cmd in pnpm python3 docker curl ffmpeg ffprobe; do
  command -v "$cmd" >/dev/null || { echo "ERROR: missing command $cmd"; exit 1; }
done

echo "[1/7] Frontend checks"
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm build

echo "[2/7] Backend checks"
services/worker/.venv/bin/pip install -r services/worker/requirements.txt
(cd services/worker && .venv/bin/pytest -v)

echo "[3/7] Docker Compose"
$COMPOSE down -v
$COMPOSE config --quiet
$COMPOSE up -d --build --wait
$COMPOSE ps

echo "[4/7] Queue real media fixture"
ffmpeg -loglevel error \
  -f lavfi -i color=c=blue:s=320x240:d=3 \
  -f lavfi -i sine=frequency=440:duration=3 \
  -c:v libx264 -c:a aac -shortest -y "$FIXTURE"

BEFORE_UPLOADS="$($COMPOSE exec -T worker sh -lc 'find /app/data/uploads -maxdepth 1 -type f -printf "%f\n" | sort')"
RESPONSE="$(curl -fsS -F "file=@$FIXTURE;filename=phase3b.mp4" -F format=webm http://localhost:8000/api/tools/convert)"
JOB_ID="$(printf '%s' "$RESPONSE" | python3 -c 'import json,sys; print(json.load(sys.stdin)["job_id"])')"
STATUS_URL="$(printf '%s' "$RESPONSE" | python3 -c 'import json,sys; print(json.load(sys.stdin)["status_url"])')"
echo "job=$JOB_ID"

echo "[5/7] Poll and verify safe status"
STATUS=pending
for attempt in $(seq 1 60); do
  curl -fsS "http://localhost:8000$STATUS_URL" -o "$STATUS_JSON"
  STATUS="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["status"])' "$STATUS_JSON")"
  echo "attempt=$attempt status=$STATUS"
  case "$STATUS" in completed|failed) break;; esac
  sleep 2
done
python3 -m json.tool "$STATUS_JSON"
[[ "$STATUS" == completed ]] || { echo "ERROR: terminal status is $STATUS"; exit 1; }
! grep -Eq '"input_files"|"output_files"|/app/data|data/uploads|data/processed' "$STATUS_JSON" || { echo "ERROR: filesystem path leaked"; exit 1; }

echo "[6/7] Download result and verify cleanup"
RESULT_URL="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["results"][0]["download_url"])' "$STATUS_JSON")"
curl -fSL "http://localhost:8000$RESULT_URL" -o "$RESULT_FILE"
test -s "$RESULT_FILE"
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 "$RESULT_FILE"
INVALID_URL="http://localhost:8000/api/tools/jobs/$JOB_ID/files/999"
HTTP_CODE="$(curl -sS -o /tmp/unividown-invalid.json -w '%{http_code}' "$INVALID_URL")"
[[ "$HTTP_CODE" == 404 ]] || { echo "ERROR: invalid result returned HTTP $HTTP_CODE"; exit 1; }
AFTER_UPLOADS="$($COMPOSE exec -T worker sh -lc 'find /app/data/uploads -maxdepth 1 -type f -printf "%f\n" | sort')"
[[ "$BEFORE_UPLOADS" == "$AFTER_UPLOADS" ]] || { echo "ERROR: upload input was not cleaned"; exit 1; }
! $COMPOSE exec -T worker sh -lc 'find /app/data/uploads -maxdepth 1 -name "*.part" -print -quit' | grep -q . || { echo "ERROR: partial upload remains"; exit 1; }

echo "[7/7] Restart recovery"
$COMPOSE stop worker
RECOVERY_JOB_ID="$(python3 - <<'PY'
import json, sqlite3
con = sqlite3.connect('data/unividown.db')
cur = con.execute(
    'INSERT INTO processing_jobs (tool_type,status,progress,input_files,output_files,parameters) VALUES (?,?,?,?,?,?)',
    ('convert','processing',25.0,json.dumps(['/app/data/uploads/missing.mp4']),None,json.dumps({'format':'mp4'})),
)
con.commit()
print(cur.lastrowid)
con.close()
PY
)"
$COMPOSE start worker
sleep 6
RECOVERY_STATUS="$(python3 - "$RECOVERY_JOB_ID" <<'PY'
import sqlite3, sys
con = sqlite3.connect('data/unividown.db')
print(con.execute('SELECT status FROM processing_jobs WHERE id=?',(int(sys.argv[1]),)).fetchone()[0])
con.close()
PY
)"
[[ "$RECOVERY_STATUS" != processing ]] || { echo "ERROR: recovered job remains processing"; exit 1; }
$COMPOSE logs --no-color worker | grep -Ei 'Recovered .*interrupted processing job' >/dev/null || { echo "ERROR: recovery log not found"; exit 1; }

echo "PASS: Phase 3B validation completed"
