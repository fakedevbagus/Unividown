# Changelog

All notable changes to Unividown are documented here.

## [Unreleased]

### Phase 2 — download recovery

- Restored the complete download lifecycle with secure results and resilient progress delivery.

### Phase 3A–3E — secure media processing

- Added secure uploads, strict MIME/parameter validation, safe status/results, restart recovery, terminal cleanup, and result UI for every media tool.

### Phase 3F — storage retention and quota

- Added configurable total storage quota enforcement with HTTP 507 responses.
- Added configurable retention cleanup across upload, download, and processed storage roots.
- Cleanup runs before uploads, at processing-worker startup, and on a configurable interval.
- Added cleanup reporting, empty-directory pruning, lifecycle regression tests, environment documentation, and one-command validation.
