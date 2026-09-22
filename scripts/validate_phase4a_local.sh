#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SETTINGS='apps/web/src/app/(dashboard)/settings/page.tsx'
TOOLS='apps/web/src/app/(dashboard)/tools/page.tsx'

echo "[1/4] Install frontend dependencies"
pnpm install --frozen-lockfile

echo "[2/4] Lint and typecheck"
pnpm lint
pnpm typecheck

echo "[3/4] Build production frontend"
pnpm build

echo "[4/4] Verify honest settings and complete tool catalog"
grep -q 'Configuration is deployment-managed' "$SETTINGS"
! grep -Eq 'Saved!|Save Settings|handleSave' "$SETTINGS"
for route in \
  /tools/video-converter \
  /tools/video-trimmer \
  /tools/audio-converter \
  /tools/image-optimizer \
  /tools/subtitle-extractor \
  /tools/gif-maker \
  /tools/transcribe \
  /tools/qr \
  /tools/password; do
  grep -q "href: '$route'" "$TOOLS" || { echo "ERROR: missing tool catalog route $route"; exit 1; }
done

echo "PASS: Phase 4A UI truth and tool catalog gate completed"
