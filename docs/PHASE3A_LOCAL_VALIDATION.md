# Phase 3A local validation — secure media uploads

Run this checklist from `fix/secure-media-uploads` after automated tests pass.

## Automated baseline

```bash
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm build
cd services/worker
.venv/bin/pytest -v
cd ../..
docker compose -f docker-compose.dev.yml up -d --build --wait
```

## Security cases

Use a small valid MP4 fixture at `/tmp/fixture.mp4`.

```bash
# A valid upload should queue and use a generated path.
curl -fsS -F 'file=@/tmp/fixture.mp4;filename=normal.mp4' \
  -F 'format=mp3' http://localhost:8000/api/tools/convert

# A traversal filename must not escape UPLOAD_DIR.
curl -fsS -F 'file=@/tmp/fixture.mp4;filename=../../escape.mp4' \
  -F 'format=mp3' http://localhost:8000/api/tools/convert

# An unsupported extension must return HTTP 415.
printf '#!/bin/sh\necho unsafe\n' >/tmp/not-media.sh
curl -sS -o /tmp/unsupported.json -w '%{http_code}\n' \
  -F 'file=@/tmp/not-media.sh' http://localhost:8000/api/tools/convert
cat /tmp/unsupported.json
```

Then inspect the mounted upload directory:

```bash
find data/uploads -maxdepth 1 -type f -printf '%f\n'
find data/uploads -name '*.part' -o -name 'escape.mp4'
```

Expected:

- Stored media names are random 32-character UUID hex values plus the validated extension.
- No `escape.mp4` exists outside or inside the upload root.
- Repeating the same client filename creates separate files instead of overwriting.
- Unsupported extension and actual MIME return HTTP 415.
- Oversized uploads return HTTP 413 and leave no `.part` file.
- An interrupted/failed multi-file upload removes files saved earlier in that request.

## Cleanup

```bash
docker compose -f docker-compose.dev.yml down -v
rm -f /tmp/not-media.sh /tmp/unsupported.json
```
