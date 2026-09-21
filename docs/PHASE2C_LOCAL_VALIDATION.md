# Phase 2C local validation

Use this checklist on the review branch before approval.

## Automated baseline

```bash
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm build

cd services/worker
.venv/bin/pytest -v
cd ../..

docker compose -f docker-compose.dev.yml config --quiet
docker compose -f docker-compose.dev.yml up -d --build --wait
curl -fsS http://localhost:8000/api/health/live
curl -fsS http://localhost:8000/api/health/ready
curl -fsS 'http://localhost:8000/socket.io/?EIO=4&transport=polling'
```

Expected: liveness reports `environment: development`, readiness is ready, and the Socket.IO payload starts with `0{`.

## Browser validation

1. Open `http://localhost:3000/download`. Confirm the queue badge says **Live updates**.
2. Submit one short public video URL with `best` quality and one short URL with `mp3` quality.
3. Confirm pending/processing progress updates, completion, and a working result-download button for each job.
4. In browser DevTools, block the worker's `/socket.io` requests or switch the browser offline briefly. Confirm the badge changes to **Polling fallback** and REST reconciliation continues every two seconds whenever HTTP remains available.
5. Restore Socket.IO access. Confirm the badge returns to **Live updates** without reloading the page.
6. Start a sufficiently long download, cancel it, and confirm it remains cancelled rather than becoming failed or completed.
7. Retry a failed/cancelled fixture where allowed and confirm only one result record/button exists for the same output path.
8. While a job is processing, restart only the worker: `docker compose -f docker-compose.dev.yml restart worker`. Confirm the job is recovered to pending and eventually resumes.

## Cleanup

```bash
docker compose -f docker-compose.dev.yml down -v
```

Do not report a pass if external media access is unavailable; report those steps as blocked with the URL/provider and error instead.
