# Phase 3F local validation — storage retention and quota

Run from the repository root:

```bash
bash scripts/validate_phase3f_local.sh
```

The runner executes the complete Phase 3 gate, verifies the documented storage environment variables, and runs focused quota/expiration lifecycle tests.

Defaults:

- `STORAGE_QUOTA_BYTES=53687091200` (50 GiB)
- `OUTPUT_RETENTION_HOURS=168` (7 days)
- `CLEANUP_INTERVAL_SECONDS=3600` (1 hour)

Set `STORAGE_QUOTA_BYTES=0` to disable quota enforcement. Cleanup runs on upload, worker startup, and periodically while the processing worker is active.

Expected final line:

```text
PASS: Phase 3F storage retention and quota validation completed
```
