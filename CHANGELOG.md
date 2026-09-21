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

### Security upgrade branch

- Upgraded Next.js to 15.5.24 and React/React DOM to 19.2.0.
- Updated React types, Next ESLint configuration, and PostCSS to patched versions.
- Converted the production web image to Next standalone output so build tooling, pnpm, and dev dependencies are excluded from runtime.

### Phase 2 — download queue reliability

- Registered `/api/downloads/info` before the dynamic job route.
- Added transactional multi-job Redis enqueue, priority/FIFO scoring, database fallback, orphan prevention, and idempotent retry.

### Phase 2 — result serving and job lifecycle

- Added contained result serving, result download actions, cooperative cancellation, startup recovery, and downloaded-file upsert.

### Phase 2C — resilient progress delivery

- Added explicit Socket.IO connection state and unlimited backoff reconnection.
- Added adaptive REST polling: two seconds while disconnected and periodic reconciliation while connected.
- Refreshes terminal job state from the API so completed file metadata appears even if a socket event omits it.
- Added a visible Live updates/Polling fallback status badge.
- Fixed liveness environment reporting to honor `PYTHON_ENV`.
- Added a PC-local validation checklist for video, audio, result download, cancellation, retry, reconnect, and restart recovery.
