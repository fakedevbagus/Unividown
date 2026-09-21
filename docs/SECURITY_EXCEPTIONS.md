# Security Exceptions

## Policy

Image scans continue to report every HIGH/CRITICAL finding. An exception is allowed only when the upstream distribution has no fixed package, the dependency is required or inherited from the supported base image, the affected runtime path has passed smoke tests, and the exception has an expiration date.

The machine-readable source is `security/trivy-exceptions.json`. `scripts/enforce_trivy_policy.py` fails CI for every unlisted or expired finding. CI runs on pull requests, pushes, and weekly so expired exceptions automatically reopen the gate.

## Active exceptions — expires 2026-10-21

The exact CVE/package pairs are stored in `security/trivy-exceptions.json`. They cover:

- Required FFmpeg runtime and codec libraries: `ffmpeg`, `libavcodec59`, and `libaom3`.
- Debian base runtime packages: `bsdutils`, `libacl1`, and `gzip`.

All entries were reported without a fixed Debian Bookworm version as of 2026-09-21. The worker base was pinned to Bookworm, `curl` was removed, health checks now use Python stdlib, and the complete worker/Compose smoke suite passed before acceptance. The policy blocks each newly disclosed CVE until its exact image/package pair is reviewed and listed; it never applies a blanket `ignore-unfixed` rule.

## Required review

Before 2026-10-21:

1. Rebuild with the latest Bookworm packages and rerun both image scans.
2. Remove each exception as soon as `FixedVersion` becomes available.
3. If no fix exists, reassess exploitability and either renew with explicit approval and a new deadline or keep the release blocked.
4. Review whether a maintained static FFmpeg build or newer Debian release reduces the exception set without destabilizing media compatibility.
