# Preparation Checklist - Unividown

## System Requirements
- [x] Node.js 20+ installed
- [x] Python 3.11+ installed
- [x] pnpm installed (`npm install -g pnpm`)
- [x] Git installed
- [x] FFmpeg installed (system-level)
- [x] yt-dlp installed (`pip install yt-dlp`)
- [x] VSCode + Cline extension installed

## Project Setup
- [x] Create project folder: `mkdir unividown && cd unividown`
- [x] Initialize git: `git init`
- [x] Create `.env` file from template (see 00-setup.md)

## Dependencies to Install Later
### Frontend (apps/web):
- next, react, react-dom, typescript
- tailwindcss, framer-motion, lucide-react
- socket.io-client, zustand, next-intl
- react-dropzone, date-fns, clsx

### Backend (services/worker):
- fastapi, uvicorn, sqlalchemy
- yt-dlp, ffmpeg-python, pillow
- python-socketio, websockets
- pytest, httpx

## Environment Variables
```
NODE_ENV=development
PORT=3000
WORKER_URL=http://localhost:8000
DATABASE_URL=sqlite:///./data/unividown.db
UPLOAD_DIR=./data/uploads
MAX_FILE_SIZE=10737418240
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60000
```

## Storage Requirements
- Minimum 20GB free space for downloads
- SSD recommended for performance
