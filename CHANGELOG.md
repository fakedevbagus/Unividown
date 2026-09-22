# Changelog

All notable changes to Unividown are documented here.

## [Unreleased]

### Phase 2 — download recovery

- Fixed metadata route order, queue fallback/atomicity, orphan prevention, priority/FIFO, and idempotent retry.
- Added contained result serving, result download actions, cooperative cancellation, restart recovery, and downloaded-file upsert.
- Added Socket.IO state, continuous reconnect, adaptive REST polling, and terminal-state reconciliation.
- Fixed liveness environment reporting to honor `PYTHON_ENV`.

### Phase 3A — secure media uploads

- Replaced client filenames with UUID-based storage names while preserving validated extensions.
- Streams uploads in bounded chunks and enforces `MAX_FILE_SIZE` during transfer.
- Validates actual MIME using libmagic and rejects unsupported extensions/types.
- Cleans partial files, failed request files, and database-failure artifacts.
- Prevents traversal, overwrite, and same-name collisions by construction.
- Added regression coverage and a PC-local security validation checklist.
