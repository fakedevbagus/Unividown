import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from app.database import Base, engine
from app.api.endpoints.downloads import router as downloads_router
from app.api.endpoints.tools import router as tools_router
from app.workers.download_worker import DownloadWorker
from app.workers.process_worker import ProcessWorker

# Setup Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
download_worker = DownloadWorker(sio=sio)
process_worker = ProcessWorker()


@sio.event
async def connect(sid, environ):
    print(f"[SIO] Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"[SIO] Client disconnected: {sid}")


@sio.event
async def join_download(sid, job_id):
    await sio.enter_room(sid, f"job:{job_id}")
    print(f"[SIO] Client {sid} joined room job:{job_id}")


@sio.event
async def leave_download(sid, job_id):
    await sio.leave_room(sid, f"job:{job_id}")
    print(f"[SIO] Client {sid} left room job:{job_id}")


# Background queue management
worker_task = None
process_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    Base.metadata.create_all(bind=engine)
    print("[Main] Database tables verified/created.")

    # Start download worker task
    global worker_task, process_task
    worker_task = asyncio.create_task(download_worker.process_queue())
    process_task = asyncio.create_task(process_worker.process_queue())
    print("[Main] Background workers started.")

    yield

    # Shutdown
    download_worker.running = False
    process_worker.running = False
    if worker_task:
        worker_task.cancel()
    if process_task:
        process_task.cancel()
    print("[Main] Workers gracefully stopped.")


app = FastAPI(
    title="Unividown Worker API",
    description="Media downloader and processing engine for Unividown",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(downloads_router, prefix="/api")
app.include_router(tools_router, prefix="/api")


@app.get("/api/status")
def get_system_status():
    return {
        "status": "online",
        "service": "unividown-worker",
        "version": "1.0.0",
    }


# Wrap FastAPI with Socket.IO ASGIApp
sio_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path="/socket.io")

