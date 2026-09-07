import asyncio
import os
import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import socketio

from app.config import settings
from app.database import Base, engine
from app.api.endpoints.downloads import router as downloads_router
from app.api.endpoints.tools import router as tools_router
from app.workers.download_worker import DownloadWorker
from app.workers.process_worker import ProcessWorker
from app.middleware.rate_limit import RateLimitMiddleware
from app.utils.logger import (
    logger, log_request, log_response, 
    log_download_event, log_processing_event,
    log_error_with_context, request_id_var
)

# Setup Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=settings.allowed_origins)
download_worker = DownloadWorker(sio=sio)
process_worker = ProcessWorker()


@sio.event
async def connect(sid, environ):
    log_download_event("websocket_connect", job_id=0, url=sid)


@sio.event
async def disconnect(sid):
    log_download_event("websocket_disconnect", job_id=0, url=sid)


@sio.event
async def join_download(sid, job_id):
    await sio.enter_room(sid, f"job:{job_id}")
    log_download_event("websocket_join", job_id=job_id, url=sid)


@sio.event
async def leave_download(sid, job_id):
    await sio.leave_room(sid, f"job:{job_id}")
    log_download_event("websocket_leave", job_id=job_id, url=sid)


# Background queue management
worker_task = None
process_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created")

    # Start download worker task
    global worker_task, process_task
    worker_task = asyncio.create_task(download_worker.process_queue())
    process_task = asyncio.create_task(process_worker.process_queue())
    logger.info("Background workers started")

    yield

    # Shutdown
    download_worker.running = False
    process_worker.running = False
    if worker_task:
        worker_task.cancel()
    if process_task:
        process_task.cancel()
    logger.info("Workers gracefully stopped")


app = FastAPI(
    title="Unividown Worker API",
    description="Media downloader and processing engine for Unividown",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS - use configured allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request_id_var.set(request_id)
    
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    log_request(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=client_ip,
        query_params=dict(request.query_params),
    )
    
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        
        log_response(
            request_id=request_id,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        
        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log_error_with_context(
            e,
            context={
                "method": request.method,
                "path": request.url.path,
                "client_ip": client_ip,
            },
            request_id=request_id
        )
        raise


# Register API routers
app.include_router(downloads_router, prefix="/api")
app.include_router(tools_router, prefix="/api")


@app.get("/api/status")
@app.get("/api/health")
def get_system_status():
    return {
        "status": "online",
        "service": "unividown-worker",
        "version": "1.0.0",
        "environment": "production" if not settings.debug else "development",
    }


# Prometheus metrics endpoint
@app.get("/metrics")
def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return Response(content=get_metrics(), media_type=get_content_type())


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = request_id_var.get()
    log_error_with_context(
        exc,
        context={
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
        },
        request_id=request_id
    )
    return Response(
        content='{"error": "Internal server error"}',
        status_code=500,
        media_type="application/json",
    )


# Wrap FastAPI with Socket.IO ASGIApp
sio_app = socketio.ASGIApp(sio, other_asgi_app=app, socketio_path="/socket.io")

