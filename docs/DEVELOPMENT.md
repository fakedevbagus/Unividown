# Development Guide

## Supported baseline

- Node.js 20 LTS (`.nvmrc`)
- pnpm 9.15.5 (`packageManager` in `package.json`)
- Python 3.11
- FFmpeg 6 or newer
- Redis 7
- Docker Engine 24+ with Compose v2 for container workflows

Newer runtimes may work but are not the verification target.

## Local setup without Docker

```bash
corepack enable
corepack prepare pnpm@9.15.5 --activate
pnpm install --frozen-lockfile

python3.11 -m venv services/worker/.venv
services/worker/.venv/bin/pip install -r services/worker/requirements.txt
cp .env.example .env
```

Start Redis when queue-backed download behavior is needed. For local API/tool work without Redis, set `REDIS_REQUIRED=false`; readiness will report degraded Redis while required checks can remain ready.

```bash
pnpm dev
cd services/worker
.venv/bin/uvicorn app.main:sio_app --reload --host 0.0.0.0 --port 8000
```

To enable transcription locally:

```bash
services/worker/.venv/bin/pip install -r services/worker/requirements-ai.txt
```

## Docker setup

Development:

```bash
docker compose -f docker-compose.dev.yml config
docker compose -f docker-compose.dev.yml up --build
```

Production-like VPS setup:

```bash
docker compose config
docker compose up -d --build
docker compose ps
```

The core worker image excludes Whisper. Build an AI-enabled worker only when transcription is required:

```bash
docker compose build --build-arg INSTALL_AI=true worker
```

Docker deployments set `REDIS_REQUIRED=true` and wait for Redis health before starting the worker.

## Verification commands

```bash
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm build

cd services/worker
.venv/bin/pytest -v
```

Runtime smoke checks:

```bash
curl -fsS http://localhost:8000/api/health/live
curl -fsS http://localhost:8000/api/health/ready
curl -fsS http://localhost:8000/metrics
curl -fsS 'http://localhost:8000/socket.io/?EIO=4&transport=polling'
```

The Socket.IO response should begin with an Engine.IO open packet (`0{...}`). Readiness returns HTTP 503 when any required dependency fails. Optional Redis failure in non-Docker local/test mode appears as degraded instead.

Docker verification:

```bash
docker build -t unividown-web:test -f docker/Dockerfile.web .
docker build -t unividown-worker:test -f docker/Dockerfile.worker .
docker run --rm -p 3000:3000 unividown-web:test
docker compose -f docker-compose.dev.yml config
docker compose config
```

## Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `WORKER_URL` | `http://localhost:8000` | Web-to-worker server URL |
| `DATABASE_URL` | `sqlite:///./data/unividown.db` | SQLAlchemy database URL |
| `UPLOAD_DIR` | `./data/uploads` | Temporary uploads |
| `DOWNLOAD_DIR` | `./data/downloads` | Download outputs |
| `PROCESSED_DIR` | `./data/processed` | Media-tool outputs |
| `MAX_FILE_SIZE` | `10737418240` | Current backend size setting |
| `REDIS_URL` | `redis://localhost:6379/0` | Queue/cache Redis URL |
| `REDIS_REQUIRED` | `false` | Whether Redis failure blocks readiness |
| `RATE_LIMIT_REQUESTS` | `60` | Rate-limit request count |
| `RATE_LIMIT_WINDOW` | `60000` | Existing rate-limit window setting |

Never commit `.env`, media, SQLite databases, data directories, virtual environments, `node_modules`, or build output.

## Troubleshooting

- **`pnpm typecheck` is missing:** update from this branch; both root and web manifests now define it.
- **Readiness is 503:** inspect `checks` in the JSON response. Confirm Redis, writable storage, FFmpeg, database access, and both background tasks.
- **Socket.IO is 404:** start `app.main:sio_app`, not `app.main:app`.
- **Transcription returns 503:** install `requirements-ai.txt` or build with `INSTALL_AI=true`.
- **Tests try Redis:** tests must mock queue calls or use an explicit Redis service. Do not silently depend on a developer machine's Redis.
- **Docker is unavailable:** validate YAML and Dockerfiles statically, then mark build/start/smoke evidence as unverified.

## Updating project logs

After every implementation session update `PROJECT_STATUS.md`, `CHANGELOG.md`, and this guide when commands/config change. Record date, branch/PR, changed files and architecture decisions, exact test results, new risks, gate status, next exact step, and the next-chat handoff prompt. Mirror the same concise evidence in the Notion recovery log.

## Download queue modes

Docker sets `REDIS_REQUIRED=true`. A failed enqueue returns HTTP 503 and the API removes the just-created database record so no orphan job remains.

Local/test mode may set `REDIS_REQUIRED=false`. When Redis is unavailable, create/batch/retry responses use `queue_backend: "database"`; the worker discovers pending records through the database fallback. Tests must mock Redis or use an explicit service and must cover both modes.
