# Changelog

All notable changes to Unividown are documented here.

## [Unreleased]

### Added

- Runtime baseline documentation, supported versions, development workflow, and pull request template.
- Root and web `typecheck` scripts.
- Separate liveness (`/api/health/live`) and readiness (`/api/health/ready`) endpoints with database, Redis, storage, FFmpeg, and background-worker checks.
- Regression tests for health behavior, Prometheus metrics, Socket.IO polling handshake, and optional transcription capability.
- Redis and service health checks in development and production Compose definitions.
- Optional AI requirements file for Whisper.
- Docker context exclusions for dependencies, build caches, data, and local environments.

### Changed

- Worker runtime now starts `app.main:sio_app` so HTTP and Socket.IO share the same ASGI entrypoint.
- Web runtime image now includes the workspace manifests and runtime dependencies required by the filtered pnpm start command.
- Metrics are imported correctly and HTTP request metrics are recorded.
- CI pins supported runtimes, supplies Redis explicitly, transfers built images to the security-scan job, and removes placeholder deployment behavior.
- Core worker dependency/image no longer installs Whisper; the transcription endpoint returns a clear 503 when the optional AI profile is absent.
- Web image setup retries transient pnpm/Corepack downloads.

### Fixed

- Missing `/metrics` imports that previously raised `NameError`.
- Missing CI `typecheck` script.
- Security scans attempting to inspect images unavailable on their runner.
- Local typecheck failures caused by stale generated `.next/types` entries from removed routes.
- Docker contexts unnecessarily transferring local `node_modules`, `.next`, data, and virtual environments.

### Deferred

- Download route order, Redis queue fallback/atomicity, uploads, result serving, and all Phase 2+ behavior remain intentionally unchanged.

### Security upgrade branch

- Upgraded Next.js to 15.5.24 and React/React DOM to 19.2.0.
- Updated React types, Next ESLint configuration, and PostCSS to patched versions.
- Converted the production web image to Next standalone output so build tooling, pnpm, and dev dependencies are excluded from runtime.
- Added Alpine package upgrades to the web base and upgraded Python packaging tools in the worker image.

### Phase 2 — download queue reliability (in review)

- Registered `/api/downloads/info` before the dynamic job route so metadata requests are no longer parsed as job IDs.
- Added transactional multi-job Redis enqueue, deterministic priority/FIFO scoring, and explicit required-Redis failures.
- Added database fallback when Redis is optional, with API responses identifying the active queue backend.
- Prevented orphan database jobs when required enqueue fails.
- Made retry idempotent for jobs already pending/processing and restored prior state when required re-enqueue fails.
- Added regression coverage for route order, fallback, required failure, orphan prevention, priority semantics, and retry idempotency.
