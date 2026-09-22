import importlib.util
import json
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.processing_job import ProcessingJob
from app.services.uploads import cleanup_uploads, save_upload
from app.utils.file_validator import validate_multipart_files

router = APIRouter(prefix="/tools", tags=["tools"])


async def queue_processing_job(files: List[UploadFile], tool_type: str, parameters: dict, db: Session) -> ProcessingJob:
    validate_multipart_files(files)
    saved_paths: List[str] = []
    try:
        for upload in files:
            saved_paths.append(await save_upload(upload))
        job = ProcessingJob(tool_type=tool_type, input_files=json.dumps(saved_paths), parameters=json.dumps(parameters), status="pending", progress=0.0)
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    except Exception:
        db.rollback()
        cleanup_uploads(saved_paths)
        raise


def queued_response(job: ProcessingJob, **extra):
    return {"job_id": job.id, "status": "queued", **extra}


@router.post("/convert")
async def convert_media(file: UploadFile = File(...), format: str = Form("mp4"), db: Session = Depends(get_db)):
    return queued_response(await queue_processing_job([file], "convert", {"format": format}, db))


@router.post("/trim")
async def trim_media(file: UploadFile = File(...), start: float = Form(0.0), end: float = Form(10.0), db: Session = Depends(get_db)):
    return queued_response(await queue_processing_job([file], "trim", {"start": start, "end": end}, db))


@router.post("/compress")
async def compress_media(file: UploadFile = File(...), bitrate: str = Form("1000k"), db: Session = Depends(get_db)):
    return queued_response(await queue_processing_job([file], "compress", {"bitrate": bitrate}, db))


@router.post("/merge")
async def merge_media(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    return queued_response(await queue_processing_job(files, "merge", {}, db))


@router.post("/audio/convert")
async def audio_convert(file: UploadFile = File(...), format: str = Form("mp3"), db: Session = Depends(get_db)):
    return queued_response(await queue_processing_job([file], "audio_convert", {"format": format}, db))


@router.post("/image/optimize")
async def image_optimize(file: UploadFile = File(...), quality: int = Form(85), max_width: int = Form(1920), db: Session = Depends(get_db)):
    return queued_response(await queue_processing_job([file], "image_optimize", {"quality": quality, "max_width": max_width}, db))


@router.post("/subtitle/extract")
async def subtitle_extract(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return queued_response(await queue_processing_job([file], "subtitle_extract", {}, db))


@router.post("/gif/make")
async def gif_make(file: UploadFile = File(...), start: float = Form(0.0), duration: float = Form(5.0), fps: int = Form(15), scale: int = Form(480), db: Session = Depends(get_db)):
    return queued_response(await queue_processing_job([file], "gif_make", {"start": start, "duration": duration, "fps": fps, "scale": scale}, db))


@router.get("/jobs")
def list_processing_jobs(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(ProcessingJob)
    if status:
        query = query.filter_by(status=status)
    return [job.to_dict() for job in query.order_by(ProcessingJob.id.desc()).limit(50).all()]


@router.get("/jobs/{job_id}")
def get_processing_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    return job.to_dict()


@router.post("/transcribe")
async def transcribe_media(file: UploadFile = File(...), model: str = Form("tiny"), db: Session = Depends(get_db)):
    if importlib.util.find_spec("whisper") is None:
        raise HTTPException(status_code=503, detail="Transcription capability unavailable. Install the optional AI profile.")
    job = await queue_processing_job([file], "transcribe", {"model": model}, db)
    return queued_response(job, model=model)
