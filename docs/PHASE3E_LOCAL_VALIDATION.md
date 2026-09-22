# Phase 3E local validation — media input and parameter validation

Run from the repository root:

```bash
bash scripts/validate_phase3e_local.sh
```

The runner reuses the complete Phase 3 backend/UI gate, checks the capabilities endpoint, and verifies that unsupported formats, invalid trim ranges, and excessive GIF duration are rejected before processing.

Expected final line:

```text
PASS: Phase 3E media tool validation completed
```
