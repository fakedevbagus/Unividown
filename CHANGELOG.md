# Changelog

All notable changes to Unividown are documented here.

## [Unreleased]

### Phase 2 — download recovery

- Fixed metadata route order, queue fallback/atomicity, orphan prevention, priority/FIFO, and idempotent retry.
- Added contained result serving, result download actions, cooperative cancellation, restart recovery, and downloaded-file upsert.
- Added Socket.IO state, continuous reconnect, adaptive REST polling, and terminal-state reconciliation.
- Fixed liveness environment reporting to honor `PYTHON_ENV`.

### Phase 3A — secure media uploads

- Replaced client filenames with UUID-based storage names and streamed size enforcement.
- Added extension/libmagic MIME validation, traversal/collision prevention, and failure cleanup.

### Phase 3B — processing status and results

- Added `status_url` to queued processing responses.
- Removed raw input/output filesystem paths from processing API responses.
- Added contained processing-result downloads with filename and size metadata.
- Added restart recovery for interrupted processing jobs.
- Cleans temporary upload inputs after processing reaches completed or failed state.
- Added regression coverage and a PC-local validation checklist.
