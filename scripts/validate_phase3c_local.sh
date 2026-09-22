#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
COMPOSE="docker compose -f docker-compose.dev.yml"
LOG_FILE="$ROOT/phase3c-compose.log"
cleanup() {
  $COMPOSE logs --no-color worker web redis >"$LOG_FILE" 2>&1 || true
  $COMPOSE down -v >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "[1/4] Reuse complete Phase 3B backend gate"
bash scripts/validate_phase3b_local.sh

echo "[2/4] Build and start UI stack"
$COMPOSE up -d --build --wait
$COMPOSE ps

echo "[3/4] Verify tool routes and integration wiring"
curl -fsS http://localhost:3000/tools/video-converter >/dev/null
curl -fsS http://localhost:3000/tools/audio-converter >/dev/null
grep -q 'ProcessingJobStatus' 'apps/web/src/app/(dashboard)/tools/video-converter/page.tsx'
grep -q 'ProcessingJobStatus' 'apps/web/src/app/(dashboard)/tools/audio-converter/page.tsx'
grep -q '/api/worker/tools/audio/convert' 'apps/web/src/app/(dashboard)/tools/audio-converter/page.tsx'
grep -q 'setTimeout(poll, 1500)' apps/web/src/hooks/use-processing-job.ts
grep -q 'Download {result.filename}' apps/web/src/components/tools/processing-job-status.tsx

echo "[4/4] PASS"
echo "PASS: Phase 3C processing results UI validation completed"
echo "Open http://localhost:3000/tools/video-converter or /tools/audio-converter before the script exits only if running it interactively with cleanup disabled."
