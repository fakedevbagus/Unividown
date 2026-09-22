# Phase 3B local validation — processing status and results

```bash
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm build
cd services/worker
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest -v
cd ../..
docker compose -f docker-compose.dev.yml up -d --build --wait
```

Submit a small valid media file to `/api/tools/convert`, retain the returned `job_id` and `status_url`, and poll the status URL until completed. Confirm the JSON never includes `input_files`, `output_files`, upload paths, or processed filesystem paths. Confirm `results[0].download_url` downloads the output. Restart the worker during a processing job and confirm it returns to pending. After terminal completion or failure, confirm the UUID upload input has been removed.

```bash
docker compose -f docker-compose.dev.yml down -v
```
