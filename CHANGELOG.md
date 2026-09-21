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

### Changed

- Worker runtime now starts `app.main:sio_app` so HTTP and Socket.IO share the same ASGI entrypoint.
- Web runtime image now includes the workspace manifests and runtime dependencies required by the filtered pnpm start command.
- Metrics are imported correctly and HTTP request metrics are recorded.
- CI pins supported runtimes, supplies Redis explicitly, transfers built images to the security-scan job, and removes placeholder deployment behavior.
- Core worker dependency/image no longer installs Whisper; the transcription endpoint returns a clear 503 when the optional AI profile is absent.

### Fixed

- Missing `/metrics` imports that previously raised `NameError`.
- Missing CI `typecheck` script.
- Security scans attempting to inspect images unavailable on their runner.

### Deferred

- Download route order, Redis queue fallback/atomicity, uploads, result serving, and all Phase 2+ behavior remain intentionally unchanged.
