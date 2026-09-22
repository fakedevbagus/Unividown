# Unividown Project Status

Last updated: 2026-09-23 Asia/Jakarta
Active branch: `feat/phase4-ui-truth-catalog`
Baseline main: `8b82620e31d2b14dc40a6af0a5a7cf2e3477e9d8`

## Phase status

| Phase | Status | Gate |
| --- | --- | --- |
| 0 — baseline, guardrails, docs | Complete | Merged |
| 1 — startup, Docker, CI, Socket.IO, metrics | Complete | Merged; runtime and security policy green |
| Security dependency upgrade | Complete | Merged; temporary unfixed worker OS exception expires 2026-10-21 |
| 2 — download recovery | Complete | Route, queue, lifecycle, secure results, Socket.IO, and polling gates passed |
| 3 — stable media tools | Complete | PR #13 merged as `8b82620`; complete fixture gate passed locally and in CI |
| 4A — honest settings and tool catalog | In review | Frontend implementation requires local and CI validation |
| 4B–7 | Deferred | Not started |

## Feature matrix

| Area | Status | Evidence / note |
| --- | --- | --- |
| Web lint/typecheck/build | Working | Phase 3 final CI passed |
| Worker regression suite | Working | 39 tests passed in the final Phase 3 local gate |
| Download lifecycle and results | Working | Secure results, cancel/retry, recovery, Socket.IO, and polling validated |
| Media processing lifecycle | Working | Status, polling, secure result downloads, input cleanup, and restart recovery validated |
| Core media tools | Working | Deterministic fixtures passed for convert, trim, audio, image, GIF, and subtitles |
| Optional transcription | Working as optional capability | Core image returns explicit HTTP 503; AI profile remains optional |
| Storage lifecycle | Working | Configurable quota, retention, startup/periodic cleanup, and upload cleanup validated |
| Settings UI | In review | Now truthfully read-only until a real settings API exists |
| Tool catalog | In review | All supported media-tool routes are represented |
| Unified download + processing history | Deferred | Next Phase 4 slice |
| Browser E2E | Deferred | Planned after Phase 4 UI states are synchronized |

## Architecture decisions

- Redis is required in Docker; local/test may use database fallback.
- FastAPI and Socket.IO share `app.main:sio_app`; REST polling remains the reconciliation path.
- Production target is Docker Compose on a VPS.
- Whisper/transcription is an optional profile and is excluded from the core image.
- Temporary uploads are cleaned automatically; output retention and aggregate quota are configurable.
- Settings remain deployment-managed until a persistent, validated settings API exists; the UI must not simulate saving.

## Latest verification

- Complete Phase 3 one-command local acceptance gate passed on the user's PC.
- PR #13 lint/test/build, Security scan, and Trivy checks passed.
- PR #13 was squash-merged to `main` as `8b82620`.
- The Phase 4A branch removes fake Settings persistence and completes the visible tool catalog.

## Known issues

- History still renders only the download queue and does not unify processing jobs.
- Phase 4 empty/loading/error/retry states and browser E2E coverage are not complete.
- Cancellation is cooperative rather than an OS-level hard kill.
- Next.js metadata and lint deprecations, Pydantic class config, `datetime.utcnow()`, and TestClient/httpx warnings remain.
- Temporary worker OS security exception expires 2026-10-21.

## Next exact step

Run `bash scripts/validate_phase4a_local.sh` and wait for PR checks. If both pass, merge Phase 4A and begin unified download and processing history.
