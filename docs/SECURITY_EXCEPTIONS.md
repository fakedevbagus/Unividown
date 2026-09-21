# Security Exceptions

## Policy

Image scans continue to record every HIGH/CRITICAL finding. A temporary exception is allowed only when the upstream distribution reports no fixed package, the dependency is inherited from the supported worker OS image, the runtime has passed smoke tests, and the exception has an expiration date.

The machine-readable source is `security/trivy-exceptions.json`. `scripts/enforce_trivy_policy.py` fails CI for:

- every finding with a fixed version,
- every application/language dependency finding,
- every web-image finding,
- every expired exception.

CI runs on pull requests, pushes, and weekly, so expiration automatically reopens the gate.

## Active exception — expires 2026-10-21

The worker image currently inherits a large set of HIGH/CRITICAL Debian Bookworm OS-package findings for which Trivy reports `fixed=unfixed`. These include FFmpeg and its codec libraries, `bsdutils`/util-linux libraries, SQLite, GLib, Expat, gzip, ACL, and other transitive runtime libraries.

The temporary exception applies only when all of these conditions match:

1. image is `worker`,
2. Trivy class is `os-pkgs`,
3. `FixedVersion` is absent,
4. current date is on or before 2026-10-21.

This is not Trivy's blanket `ignore-unfixed` mode: findings remain in the JSON reports and job summary, while the repository policy script decides whether each one is blocking. The worker base is pinned to Debian Bookworm, `curl` was removed, health checks use Python stdlib, and the full worker/Compose smoke suite passed.

## Required review

Before 2026-10-21:

1. Rebuild with the latest Bookworm packages and rerun both image scans.
2. Confirm no fixed OS finding or application dependency is being excepted.
3. Evaluate a maintained static FFmpeg image/binary or newer Debian release to reduce inherited findings.
4. Remove the exception when upstream fixes are available; otherwise renew only with explicit approval and a new deadline.
