#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[1/3] Run complete Phase 3 validation baseline"
bash scripts/validate_phase3e_local.sh

echo "[2/3] Verify storage lifecycle configuration and tests"
grep -q 'STORAGE_QUOTA_BYTES' .env.example
grep -q 'OUTPUT_RETENTION_HOURS' .env.example
grep -q 'CLEANUP_INTERVAL_SECONDS' .env.example
(cd services/worker && .venv/bin/pytest -q tests/test_storage_lifecycle.py)

echo "[3/3] PASS"
echo "PASS: Phase 3F storage retention and quota validation completed"
