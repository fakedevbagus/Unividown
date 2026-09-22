# Phase 3A local validation — secure media uploads

Run this checklist from `fix/secure-media-upload-hardening` after automated tests pass.

```bash
pnpm install --frozen-lockfile
pnpm lint
pnpm typecheck
pnpm build
cd services/worker
.venv/bin/pip install -r requirements.txt
.venv/bin/pytest -v
cd ../..
docker compose -f docker-compose.dev.yml up -d --build --wait
```

Use a small valid MP4 fixture at `/tmp/fixture.mp4`, then validate normal upload, a `../../escape.mp4` client filename, repeated client filenames, unsupported extensions, spoofed MIME, empty files, and absence of `.part` files. Expected results: UUID storage names, no traversal/overwrite, HTTP 400/413/415 for invalid input, and cleanup after failure.

```bash
docker compose -f docker-compose.dev.yml down -v
```
