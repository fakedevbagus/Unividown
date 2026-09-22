# Changelog

All notable changes to Unividown are documented here.

## [Unreleased]

### Phase 2 — download recovery

- Restored the complete download lifecycle with secure results and resilient progress delivery.

### Phase 3A–3B — secure processing backend

- Added secure uploads, safe processing status, contained result downloads, restart recovery, and terminal cleanup.

### Phase 3C — core processing results UI

- Added reusable terminal-aware polling and shared progress/error/result rendering.
- Connected video and audio converter pages and corrected the dedicated audio endpoint.

### Phase 3D — remaining processing tools UI

- Connected video trimming, image optimization, subtitle extraction, GIF creation, and optional transcription to the shared processing lifecycle.
- Added a reusable processing-submit hook with backend error details.
- Every media tool page now follows queued jobs to terminal state and exposes downloadable results when available.
- Added a one-command local validation runner.
