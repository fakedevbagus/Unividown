# Phase 01: Project Initialization

## Objective
Setup monorepo structure dengan Next.js dan FastAPI.

## Steps

### 1. Create Monorepo Structure
```bash
mkdir -p apps/web services/worker packages/shared docker docs data
```

### 2. Initialize Root Package
Create `package.json`:
```json
{
  "name": "unividown",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "pnpm --filter @unividown/web dev",
    "build": "pnpm --filter @unividown/web build",
    "worker:dev": "cd services/worker && uvicorn app.main:app --reload --port 8000",
    "lint": "pnpm --filter @unividown/web lint",
    "test": "pnpm --filter @unividown/web test"
  }
}
```

### 3. Create pnpm-workspace.yaml
```yaml
packages:
  - 'apps/*'
  - 'services/*'
  - 'packages/*'
```

### 4. Initialize Next.js (apps/web)
```bash
cd apps/web
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --use-pnpm
pnpm add framer-motion lucide-react socket.io-client zustand next-intl react-dropzone date-fns clsx tailwind-merge
pnpm dlx shadcn-ui@latest init
```

### 5. Initialize FastAPI (services/worker)
```bash
cd services/worker
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn[standard] sqlalchemy aiosqlite yt-dlp ffmpeg-python pillow python-socketio websockets pytest
pip freeze > requirements.txt
```

### 6. Create .gitignore
Exclude: node_modules, .next, dist, .venv, __pycache__, .env, data/*

### 7. Create .env.example
```
NODE_ENV=development
PORT=3000
WORKER_URL=http://localhost:8000
DATABASE_URL=sqlite:///./data/unividown.db
UPLOAD_DIR=./data/uploads
MAX_FILE_SIZE=10737418240
```

## Expected Output
- Project structure created
- Both apps can start independently
- No dependency conflicts
