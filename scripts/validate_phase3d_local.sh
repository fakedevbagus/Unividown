#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[1/3] Run complete processing UI baseline"
bash scripts/validate_phase3c_local.sh

echo "[2/3] Verify remaining tool integrations"
for page in video-trimmer image-optimizer subtitle-extractor gif-maker transcribe; do
  file="apps/web/src/app/(dashboard)/tools/$page/page.tsx"
  test -f "$file"
  grep -q 'ProcessingJobStatus' "$file"
  grep -q 'useProcessingSubmit' "$file"
done
grep -q '/api/worker/tools/trim' 'apps/web/src/app/(dashboard)/tools/video-trimmer/page.tsx'
grep -q '/api/worker/tools/image/optimize' 'apps/web/src/app/(dashboard)/tools/image-optimizer/page.tsx'
grep -q '/api/worker/tools/subtitle/extract' 'apps/web/src/app/(dashboard)/tools/subtitle-extractor/page.tsx'
grep -q '/api/worker/tools/gif/make' 'apps/web/src/app/(dashboard)/tools/gif-maker/page.tsx'
grep -q '/api/worker/tools/transcribe' 'apps/web/src/app/(dashboard)/tools/transcribe/page.tsx'

echo "[3/3] PASS"
echo "PASS: Phase 3D remaining processing tools UI validation completed"
