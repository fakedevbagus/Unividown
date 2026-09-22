# Phase 3B local validation — processing status and results

Run the complete automated local gate from the repository root:

```bash
bash scripts/validate_phase3b_local.sh
```

The script performs frozen install, frontend lint/typecheck/build, backend tests, Docker Compose build/start, real FFmpeg fixture processing, status polling, path-leak checks, result download, invalid-result rejection, terminal upload cleanup, restart recovery, and final cleanup. It writes Compose logs to `phase3b-compose.log`.

Expected final line:

```text
Phase 3B validation passed. Logs: .../phase3b-compose.log
```
