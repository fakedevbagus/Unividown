# Unividown Project Status

Last updated: 2026-09-21 22:35 Asia/Jakarta  
Active branch: `chore/security-dependency-upgrades`  
Baseline main: `2060d00e5366e672fcbaf98d00f79266b45abd7c`

## Phase status

| Phase | Status | Gate |
| --- | --- | --- |
| 0 — baseline, guardrails, docs | Complete in review branch | Documentation and PR evidence prepared |
| 1 — startup, Docker, CI, Socket.IO, metrics | Complete in security-upgrade review branch | Runtime, Docker/Compose, tests, and security policy are green |
| Security dependency upgrade | Complete in draft PR #2 | Framework/runtime upgrades and image scans pass |
| 2 — download lifecycle | Deferred | Route conflict and Redis failure semantics intentionally unchanged |
| 3–7 | Deferred | Not started |

## Feature matrix

| Area | Status | Evidence / note |
| --- | --- | --- |
| Web lint | Working with known warnings | Two pre-existing image `alt` warnings |
| Web typecheck | Working | Deterministic clean typecheck passed |
| Web production build | Working | Next.js 15.5.24 + React 19.2.0 build passed |
| Worker unit/API tests | Working | 10 tests passed in CI on Python 3.11 |
| FastAPI liveness | Working | `/api/health/live` regression and Compose smoke passed |
| Dependency readiness | Working | Required failure returns 503; healthy Compose readiness returns 200 |
| Prometheus metrics | Working | Format and runtime smoke passed |
| Socket.IO runtime | Working | Polling handshake passed in tests and Compose smoke |
| Docker images | Working in CI | Worker core and standalone web production images build successfully |
| Docker Compose runtime | Working in CI | Dev/production config and full Redis/worker/web smoke passed |
| Image security policy | Working | Filesystem and image scans pass; expiring worker OS exception is enforced |
| Core worker without Whisper | Working | Core image starts without Whisper; unavailable endpoint returns 503 |
| Download create without Redis | Broken / Phase 2 | Existing enqueue transaction/fallback behavior is unchanged |
| `/api/downloads/info` | Broken / Phase 2 | Existing route-order conflict is unchanged |
| Processing results UI | Deferred | Phase 3–4 |

## Architecture decisions

- Docker deployments require Redis (`REDIS_REQUIRED=true`); local/test may run with degraded optional Redis readiness.
- Runtime entrypoint is `app.main:sio_app` so FastAPI and Socket.IO share one ASGI server.
- Node 20, pnpm 9.15.5, Python 3.11, FFmpeg, and Redis 7 are the supported baseline.
- Web runtime uses Next standalone output and excludes npm, pnpm, Corepack, dev dependencies, and workspace build tooling.
- Worker runtime removes pip/setuptools/wheel build tooling after dependency installation.
- Whisper is optional and excluded from the core worker image.
- Unfixed Debian worker OS findings have an explicit exception expiring 2026-10-21; fixed OS findings, language packages, and web findings remain blocking.
- Production remains Docker Compose on a VPS; deployment automation is intentionally disabled until credentials and rollback procedures exist.

## Latest verification

| Command/check | Result |
| --- | --- |
| Frozen pnpm install | Passed |
| Web lint | Passed with 2 pre-existing accessibility warnings |
| Web typecheck | Passed |
| Next.js 15.5.24 production build | Passed |
| Backend pytest | 10 passed |
| Worker/web Docker image builds | Passed |
| Dev and production Compose config | Passed |
| Full development Compose smoke | Passed |
| Liveness/readiness/metrics/Socket.IO/web HTTP | Passed |
| Trivy filesystem scan | Passed |
| Worker/web image security policy | Passed |

## Known issues

### P0/P1 deferred to Phase 2+

- `/api/downloads/info` conflicts with `/{job_id}`.
- Enqueue errors can leave database jobs behind; download worker fallback is interrupted by Redis errors.
- Upload filename/path validation and result serving remain unresolved.

### Quality debt

- Pydantic class config, `datetime.utcnow()`, TestClient/httpx, Next.js metadata, and two image accessibility warnings remain.
- Temporary worker OS security exception must be reviewed before 2026-10-21.

## Next exact step

Review draft PR #2 and merge only after explicit user approval. After the cumulative security-upgrade candidate is merged, create a fresh Phase 2 branch from updated `main`; do not begin Phase 2 on an unmerged stack.
