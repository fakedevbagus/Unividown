#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
COMPOSE="docker compose -f docker-compose.dev.yml"
cleanup(){ $COMPOSE down -v >/dev/null 2>&1 || true; rm -f /tmp/unividown-invalid.mp4; }
trap cleanup EXIT

echo "[1/4] Run complete Phase 3 UI/backend gate"
bash scripts/validate_phase3d_local.sh

echo "[2/4] Start stack for negative API validation"
$COMPOSE up -d --build --wait
printf 'invalid fixture' >/tmp/unividown-invalid.mp4

echo "[3/4] Validate capabilities and parameter rejection"
curl -fsS http://localhost:8000/api/tools/capabilities | python3 -m json.tool
CODE="$(curl -sS -o /tmp/unividown-invalid-response.json -w '%{http_code}' -F 'file=@/tmp/unividown-invalid.mp4' -F 'format=exe' http://localhost:8000/api/tools/convert)"
[[ "$CODE" == 422 ]] || { echo "ERROR: invalid format returned HTTP $CODE"; exit 1; }
CODE="$(curl -sS -o /tmp/unividown-invalid-response.json -w '%{http_code}' -F 'file=@/tmp/unividown-invalid.mp4' -F 'start=10' -F 'end=5' http://localhost:8000/api/tools/trim)"
[[ "$CODE" == 422 ]] || { echo "ERROR: invalid trim range returned HTTP $CODE"; exit 1; }
CODE="$(curl -sS -o /tmp/unividown-invalid-response.json -w '%{http_code}' -F 'file=@/tmp/unividown-invalid.mp4' -F 'duration=31' http://localhost:8000/api/tools/gif/make)"
[[ "$CODE" == 422 ]] || { echo "ERROR: invalid GIF duration returned HTTP $CODE"; exit 1; }

echo "[4/4] PASS"
echo "PASS: Phase 3E media tool validation completed"
