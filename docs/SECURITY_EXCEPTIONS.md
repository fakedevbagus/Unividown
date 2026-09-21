# Security Exceptions

## Policy

Image scans continue to report every HIGH/CRITICAL finding. An exception is allowed only when the upstream distribution has no fixed package, the dependency is required, the affected runtime path has passed smoke tests, and the exception has an expiration date.

The machine-readable source is `security/trivy-exceptions.json`. `scripts/enforce_trivy_policy.py` fails CI for every unlisted or expired finding. CI runs on pull requests, pushes, and weekly so expired exceptions automatically reopen the gate.

## Active exceptions — expires 2026-10-21

- FFmpeg: `CVE-2026-75146`, `CVE-2026-75144`, `CVE-2026-75143`, `CVE-2026-75142`, `CVE-2026-70632`, `CVE-2026-70628`, `CVE-2026-66040`, `CVE-2026-66039`, `CVE-2026-66036`, `CVE-2026-64835`, `CVE-2026-64834`, `CVE-2026-64833`, `CVE-2026-64832`, `CVE-2026-64830`, `CVE-2026-58049`.
- Debian `bsdutils`: `CVE-2026-78410`, `CVE-2026-78409`, `CVE-2026-78408`, `CVE-2026-76642`, `CVE-2026-53613`.

All are reported without a fixed Debian Bookworm version as of 2026-09-21. The worker base was pinned to Bookworm, `curl` was removed, health checks now use Python stdlib, and the complete download-worker runtime/Compose smoke suite passed before acceptance. The second Trivy run disclosed ten additional FFmpeg IDs; the policy correctly blocked them until they were reviewed and explicitly listed.

## Required review

Before 2026-10-21:

1. Rebuild with the latest Bookworm packages and rerun both image scans.
2. Remove each exception as soon as `FixedVersion` becomes available.
3. If no fix exists, reassess exploitability and either renew with explicit approval and a new deadline or keep the release blocked.
4. Never convert this list into a blanket `ignore-unfixed` rule.
