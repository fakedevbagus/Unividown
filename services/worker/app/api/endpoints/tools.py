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
