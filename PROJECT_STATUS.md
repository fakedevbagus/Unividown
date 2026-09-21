# Unividown Project Status

Last updated: 2026-09-21 19:00 Asia/Jakarta  
Active branch: `chore/baseline-runtime-recovery`  
Baseline main: `2060d00e5366e672fcbaf98d00f79266b45abd7c`

## Phase status

| Phase | Status | Gate |
| --- | --- | --- |
| 0 — baseline, guardrails, docs | Complete in review branch | Documentation and PR evidence prepared |
| 1 — startup, Docker, CI, Socket.IO, metrics | Implemented; CI/Compose smoke rerun pending | Local checks and CI image builds pass; security findings and full Compose smoke remain open |
| 2 — download lifecycle | Deferred | Route conflict and Redis failure semantics intentionally unchanged |
| 3–7 | Deferred | Not started |

## Feature matrix

| Area | Status | Evidence / note |
| --- | --- | --- |
| Web lint | Working with known warnings | Two pre-existing image `alt` warnings |
| Web typecheck | Working | `tsc --noEmit` added and passed |
| Web production build | Working | Next.js build passed; metadata warnings remain |
| Worker unit/API tests | Working | 10 passed on Python 3.13 validation host; CI targets Python 3.11 |
| FastAPI liveness | Working | `/api/health/live` regression test passed |
| Dependency readiness | Working | Required failure returns 503; Redis can be optional for local/test |
| Prometheus metrics | Working | Imports fixed, request wiring added, format regression test passed |
| Socket.IO runtime | Working in test | ASGI polling handshake against `sio_app` passed |
| Docker images | Working in CI | Worker core and web production images built successfully on PR #1 |
| Docker Compose runtime | Pending CI rerun | Config and full dev smoke were added after the first successful image builds |
| Core worker without Whisper | Working in test | Whisper removed from core requirements; unavailable endpoint returns 503 |
| Download create without Redis | Broken / Phase 2 | Existing enqueue transaction/fallback behavior is unchanged |
| `/api/downloads/info` | Broken / Phase 2 | Existing route-order conflict is unchanged |
| Processing results UI | Deferred | Phase 3–4 |

## Architecture decisions

- Docker deployments require Redis (`REDIS_REQUIRED=true`); local/test may run with degraded optional Redis readiness.
- Runtime entrypoint is `app.main:sio_app` so FastAPI and Socket.IO share one ASGI server.
- Node 20, pnpm 9.15.5, Python 3.11, FFmpeg 6+, and Redis 7 are the supported baseline.
- Whisper is an optional AI dependency in `requirements-ai.txt`; the core image does not install it.
- Production remains Docker Compose on a VPS; deployment automation is intentionally disabled until credentials and rollback procedures exist.

## Latest verification

| Command/check | Result |
| --- | --- |
| `pnpm install --frozen-lockfile` | Passed with pinned pnpm; validation host uses unsupported Node 24 warning |
| Web lint | Passed with 2 pre-existing warnings |
| Web typecheck | Passed |
| Web build | Passed with pre-existing metadata warnings |
| `pytest -q` | 10 passed, 59 deprecation warnings |
| Liveness/readiness/metrics/Socket.IO regression tests | Passed |
| Compose YAML parse | Passed for dev and production |
| Worker/web Docker image builds | Passed in GitHub Actions |
| Trivy image scan | Executed against transferred worker image; failed on HIGH/CRITICAL findings pending triage |
| `docker compose config` / compose smoke | Added to CI; rerun pending |

## Known issues

### P0/P1 deferred to Phase 2+

- `/api/downloads/info` conflicts with `/{job_id}`.
- Enqueue errors can leave database jobs behind; download worker fallback is interrupted by Redis errors.
- Upload filename/path validation and result serving remain unresolved.

### Quality debt

- Pydantic class config, `datetime.utcnow()`, TestClient/httpx, Next.js metadata, and two image accessibility warnings emit deprecations/warnings.
- Docker runner startup is corrected structurally but still requires execution in CI or a Docker-capable host.

## Next exact step

Review the rerun of draft PR #1. Confirm the newly added Compose config/up smoke step passes. Triage the worker-image HIGH/CRITICAL Trivy findings without suppressing them. On a Docker-capable host, independently run `docker compose -f docker-compose.dev.yml up --build`, verify Redis/worker/web health, call the Socket.IO polling handshake, and record container startup evidence. Do not start Phase 2 until this evidence is reviewed and the Phase 1 gate is approved.
