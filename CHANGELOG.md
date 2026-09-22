# Changelog

All notable changes to Unividown are documented here.

## [Unreleased]

### Phase 2 — download recovery

- Restored the complete download lifecycle with secure results and resilient progress delivery.

### Phase 3A–3D — secure media processing

- Added secure UUID uploads, actual MIME validation, safe processing status/results, restart recovery, terminal cleanup, and result UI for every media tool.

### Phase 3E — media input and parameter validation

- Added per-tool actual-MIME policies for video, audio, image, subtitle, GIF, and transcription inputs.
- Added strict allowlists for video/audio output formats and Whisper models.
- Added bounds and cross-field validation for trim, image quality/width, GIF timing/FPS/scale, merge file count, and compression bitrate.
- Added a capabilities endpoint describing supported formats and optional transcription availability.
- Added negative regression coverage and a one-command validation runner.
