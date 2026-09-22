import importlib.util
import json
import re
from pathlib import Path
from typing import Collection, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.processing_job import ProcessingJob
from app.services.uploads import cleanup_uploads, save_upload
from app.utils.file_validator import ALLOWED_AUDIO_TYPES, ALLOWED_IMAGE_TYPES, ALLOWED_VIDEO_TYPES, validate_multipart_files

router = APIRouter(prefix="/tools", tags=["tools"])
VIDEO_FORMATS = {"mp4", "mkv", "webm", "avi", "mov"}
AUDIO_FORMATS = {"mp3", "wav", "flac", "ogg", "aac"}
WHISPER_MODELS = {"tiny", "base", "small", "medium", "large"}
BITRATE_PATTERN = re.compile(r"^[1-9][0-9]*(?:k|K|m|M)$")


def require_choice(value: str, allowed: Collection[str], field: str) -> str:
    normalized = value.lower().strip().lstrip(".")
    if normalized not in allowed:
        raise HTTPException(status_code=422, detail=f"Unsupported {field}: {value}")
    return normalized


def parse_paths(raw_value: Optional[str]) -> List[str]:
    if not raw_value:
        return []
    try:
        value = json.loads(raw_value)
    except (TypeError, json.JSONDecodeError):
        return []
    return [str(item) for item in value] if isinstance(value, list) else []


def serialize_processing_job(job: ProcessingJob) -> dict:
    results = []
    for index, stored_path in enumerate(parse_paths(job.output_files)):
        candidate = Path(stored_path)
        results.append({"index": index, "filename": candidate.name, "file_size": candidate.stat().st_size if candidate.is_file() else None, "download_url": f"/api/tools/jobs/{job.id}/files/{index}"})
    try:
        parameters = json.loads(job.parameters) if job.parameters else {}
    except json.JSONDecodeError:
        parameters = {}
    return {"id": job.id, "tool_type": job.tool_type, "status": job.status, "progress": job.progress, "parameters": parameters, "error_message": job.error_message, "created_at": job.created_at.isoformat() if job.created_at else None, "results": results}


async def queue_processing_job(files: List[UploadFile], tool_type: str, parameters: dict, db: Session, allowed_types: Collection[str]) -> ProcessingJob:
    validate_multipart_files(files)
    saved_paths: List[str] = []
    try:
        for upload in files:
            saved_paths.append(await save_upload(upload, allowed_types=allowed_types))
        job = ProcessingJob(tool_type=tool_type, input_files=json.dumps(saved_paths), parameters=json.dumps(parameters), status="pending", progress=0.0)
        db.add(job); db.commit(); db.refresh(job)
        return job
    except Exception:
        db.rollback(); cleanup_uploads(saved_paths); raise


def queued_response(job: ProcessingJob, **extra):
    return {"job_id": job.id, "status": "queued", "status_url": f"/api/tools/jobs/{job.id}", **extra}


@router.get("/capabilities")
def get_tool_capabilities():
    return {"video_formats": sorted(VIDEO_FORMATS), "audio_formats": sorted(AUDIO_FORMATS), "whisper_models": sorted(WHISPER_MODELS), "transcription_available": importlib.util.find_spec("whisper") is not None}


@router.post("/convert")
async def convert_media(file: UploadFile = File(...), format: str = Form("mp4"), db: Session = Depends(get_db)):
    output = require_choice(format, VIDEO_FORMATS, "video format")
    return queued_response(await queue_processing_job([file], "convert", {"format": output}, db, ALLOWED_VIDEO_TYPES))


@router.post("/trim")
async def trim_media(file: UploadFile = File(...), start: float = Form(0.0, ge=0), end: float = Form(10.0, gt=0), db: Session = Depends(get_db)):
    if end <= start:
        raise HTTPException(status_code=422, detail="End time must be greater than start time")
    return queued_response(await queue_processing_job([file], "trim", {"start": start, "end": end}, db, ALLOWED_VIDEO_TYPES))


@router.post("/compress")
async def compress_media(file: UploadFile = File(...), bitrate: str = Form("1000k"), db: Session = Depends(get_db)):
    if not BITRATE_PATTERN.fullmatch(bitrate.strip()):
        raise HTTPException(status_code=422, detail="Invalid bitrate; use values such as 1000k or 2M")
    return queued_response(await queue_processing_job([file], "compress", {"bitrate": bitrate.strip()}, db, ALLOWED_VIDEO_TYPES))


@router.post("/merge")
async def merge_media(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    if len(files) < 2:
        raise HTTPException(status_code=422, detail="Merge requires at least two files")
    return queued_response(await queue_processing_job(files, "merge", {}, db, ALLOWED_VIDEO_TYPES))


@router.post("/audio/convert")
async def audio_convert(file: UploadFile = File(...), format: str = Form("mp3"), db: Session = Depends(get_db)):
    output = require_choice(format, AUDIO_FORMATS, "audio format")
    return queued_response(await queue_processing_job([file], "audio_convert", {"format": output}, db, ALLOWED_AUDIO_TYPES | ALLOWED_VIDEO_TYPES))


@router.post("/image/optimize")
async def image_optimize(file: UploadFile = File(...), quality: int = Form(85, ge=1, le=100), max_width: int = Form(1920, ge=64, le=8192), db: Session = Depends(get_db)):
    return queued_response(await queue_processing_job([file], "image_optimize", {"quality": quality, "max_width": max_width}, db, ALLOWED_IMAGE_TYPES))


@router.post("/subtitle/extract")
async def subtitle_extract(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return queued_response(await queue_processing_job([file], "subtitle_extract", {}, db, ALLOWED_VIDEO_TYPES))


@router.post("/gif/make")
async def gif_make(file: UploadFile = File(...), start: float = Form(0.0, ge=0), duration: float = Form(5.0, ge=0.1, le=30), fps: int = Form(15, ge=1, le=60), scale: int = Form(480, ge=64, le=1920), db: Session = Depends(get_db)):
    params = {"start": start, "duration": duration, "fps": fps, "scale": scale}
    return queued_response(await queue_processing_job([file], "gif_make", params, db, ALLOWED_VIDEO_TYPES))


@router.get("/jobs")
def list_processing_jobs(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ProcessingJob)
    if status:
        query = query.filter_by(status=status)
    return [serialize_processing_job(job) for job in query.order_by(ProcessingJob.id.desc()).limit(50).all()]


@router.get("/jobs/{job_id}")
def get_processing_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    return serialize_processing_job(job)


@router.get("/jobs/{job_id}/files/{file_index}")
def get_processing_result(job_id: int, file_index: int, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    paths = parse_paths(job.output_files)
    if file_index < 0 or file_index >= len(paths):
        raise HTTPException(status_code=404, detail="Result file not found")
    root = Path(settings.processed_dir).resolve(); candidate = Path(paths[file_index]).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as error:
        raise HTTPException(status_code=404, detail="Result file not available") from error
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="Result file not available")
    return FileResponse(candidate, filename=candidate.name, media_type="application/octet-stream")


@router.post("/transcribe")
async def transcribe_media(file: UploadFile = File(...), model: str = Form("tiny"), db: Session = Depends(get_db)):
    selected_model = require_choice(model, WHISPER_MODELS, "Whisper model")
    if importlib.util.find_spec("whisper") is None:
        raise HTTPException(status_code=503, detail="Transcription capability unavailable. Install the optional AI profile.")
    job = await queue_processing_job([file], "transcribe", {"model": selected_model}, db, ALLOWED_AUDIO_TYPES | ALLOWED_VIDEO_TYPES)
    return queued_response(job, model=selected_model)
