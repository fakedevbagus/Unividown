import json
import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.processing_job import ProcessingJob

router = APIRouter(prefix="/tools", tags=["tools"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./data/uploads")).resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def save_upload(file: UploadFile) -> str:
    destination = UPLOAD_DIR / file.filename
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return str(destination)


@router.post("/convert")
async def convert_media(
    file: UploadFile = File(...),
    format: str = Form("mp4"),
    db: Session = Depends(get_db),
):
    saved_path = await save_upload(file)
    job = ProcessingJob(
        tool_type="convert",
        input_files=json.dumps([saved_path]),
        parameters=json.dumps({"format": format}),
        status="pending",
        progress=0.0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": job.id, "status": "queued"}


@router.post("/trim")
async def trim_media(
    file: UploadFile = File(...),
    start: float = Form(0.0),
    end: float = Form(10.0),
    db: Session = Depends(get_db),
):
    saved_path = await save_upload(file)
    job = ProcessingJob(
        tool_type="trim",
        input_files=json.dumps([saved_path]),
        parameters=json.dumps({"start": start, "end": end}),
        status="pending",
        progress=0.0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": job.id, "status": "queued"}


@router.post("/compress")
async def compress_media(
    file: UploadFile = File(...),
    bitrate: str = Form("1000k"),
    db: Session = Depends(get_db),
):
    saved_path = await save_upload(file)
    job = ProcessingJob(
        tool_type="compress",
        input_files=json.dumps([saved_path]),
        parameters=json.dumps({"bitrate": bitrate}),
        status="pending",
        progress=0.0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": job.id, "status": "queued"}


@router.post("/merge")
async def merge_media(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    saved_paths = []
    for f in files:
        path = await save_upload(f)
        saved_paths.append(path)

    job = ProcessingJob(
        tool_type="merge",
        input_files=json.dumps(saved_paths),
        parameters=json.dumps({}),
        status="pending",
        progress=0.0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": job.id, "status": "queued"}


# Phase 16: New tool endpoints
@router.post("/audio/convert")
async def audio_convert(
    file: UploadFile = File(...),
    format: str = Form("mp3"),
    db: Session = Depends(get_db),
):
    """Extract/convert audio from video"""
    saved_path = await save_upload(file)
    job = ProcessingJob(
        tool_type="audio_convert",
        input_files=json.dumps([saved_path]),
        parameters=json.dumps({"format": format}),
        status="pending",
        progress=0.0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": job.id, "status": "queued"}


@router.post("/image/optimize")
async def image_optimize(
    file: UploadFile = File(...),
    quality: int = Form(85),
    max_width: int = Form(1920),
    db: Session = Depends(get_db),
):
    """Optimize image for web"""
    saved_path = await save_upload(file)
    job = ProcessingJob(
        tool_type="image_optimize",
        input_files=json.dumps([saved_path]),
        parameters=json.dumps({"quality": quality, "max_width": max_width}),
        status="pending",
        progress=0.0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": job.id, "status": "queued"}


@router.post("/subtitle/extract")
async def subtitle_extract(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Extract subtitles from video"""
    saved_path = await save_upload(file)
    job = ProcessingJob(
        tool_type="subtitle_extract",
        input_files=json.dumps([saved_path]),
        parameters=json.dumps({}),
        status="pending",
        progress=0.0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": job.id, "status": "queued"}


@router.post("/gif/make")
async def gif_make(
    file: UploadFile = File(...),
    start: float = Form(0.0),
    duration: float = Form(5.0),
    fps: int = Form(15),
    scale: int = Form(480),
    db: Session = Depends(get_db),
):
    """Create GIF from video"""
    saved_path = await save_upload(file)
    job = ProcessingJob(
        tool_type="gif_make",
        input_files=json.dumps([saved_path]),
        parameters=json.dumps({"start": start, "duration": duration, "fps": fps, "scale": scale}),
        status="pending",
        progress=0.0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": job.id, "status": "queued"}


@router.get("/jobs")
def list_processing_jobs(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(ProcessingJob)
    if status:
        query = query.filter_by(status=status)
    jobs = query.order_by(ProcessingJob.id.desc()).limit(50).all()
    return [j.to_dict() for j in jobs]


@router.get("/jobs/{job_id}")
def get_processing_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Processing job not found")
    return job.to_dict()


@router.post("/transcribe")
async def transcribe_media(
    file: UploadFile = File(...),
    model: str = Form("tiny"),
    db: Session = Depends(get_db),
):
    """Transcribe audio/video to text using Whisper"""
    saved_path = await save_upload(file)
    job = ProcessingJob(
        tool_type="transcribe",
        input_files=json.dumps([saved_path]),
        parameters=json.dumps({"model": model}),
        status="pending",
        progress=0.0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"job_id": job.id, "status": "queued", "model": model}
