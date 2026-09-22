# Changelog

All notable changes to Unividown are documented here.

## [Unreleased]

### Phase 2 — download recovery

- Fixed route order, queue reliability, secure result serving, lifecycle recovery, and resilient progress delivery.

### Phase 3A — secure media uploads

- Added UUID upload storage, streaming limits, extension/libmagic validation, traversal/collision prevention, and cleanup.

### Phase 3B — processing status and results

- Added safe processing status, contained result downloads, restart recovery, terminal input cleanup, and one-command validation.

### Phase 3C — processing results UI

- Added a reusable processing-job polling hook that stops at terminal state.
- Added a shared status/progress/error/result-download component.
- Connected video and audio converter pages to live processing state and downloadable results.
- Corrected the audio converter to use `/tools/audio/convert` instead of the generic video conversion endpoint.
- Added a one-command local validation runner.
