# Changelog

All notable changes to Unividown are documented here.

## [Unreleased]

### Added

- Runtime baseline documentation, supported versions, development workflow, and pull request template.
- Root and web `typecheck` scripts.
- Separate liveness (`/api/health/live`) and readiness (`/api/health/ready`) endpoints with dependency checks.
- Regression tests for runtime, queue, lifecycle, and secure uploads.
- Redis and service health checks in development and production Compose definitions.
- Optional AI requirements file for Whisper.

### Changed

- Worker runtime starts `app.main:sio_app` so HTTP and Socket.IO share one ASGI entrypoint.
- CI pins supported runtimes, supplies Redis, transfers images to security scanning, and enforces image policy.
- Core worker excludes Whisper; transcription returns a clear 503 when the optional profile is absent.
- Web production image uses Next standalone output.

### Phase 2 — download recovery

- Fixed metadata route order, queue fallback/atomicity, orphan prevention, priority/FIFO, and idempotent retry.
- Added contained result serving, result download actions, cooperative cancellation, restart recovery, and downloaded-file upsert.
- Added explicit Socket.IO state, continuous reconnect, adaptive REST polling, and terminal-state reconciliation.
- Fixed liveness environment reporting to honor `PYTHON_ENV`.

### Phase 3A — secure media uploads

- Replaced client filenames with UUID-based storage names while preserving validated extensions.
- Streams uploads in bounded chunks and enforces `MAX_FILE_SIZE` during transfer.
- Validates actual MIME using libmagic after upload and rejects unsupported extensions/types.
- Cleans partial files, failed request files, and database-failure artifacts.
- Prevents traversal, overwrite, and same-name collisions by construction.
- Added regression coverage and a PC-local security validation checklist.
