from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.download_job import DownloadJob
from app.models.downloaded_file import DownloadedFile
from app.services.downloader import Downloader
from app.queue.redis_queue import queue

router = APIRouter(prefix="/downloads", tags=["downloads"])
downloader_service = Downloader()


class CreateDownloadRequest(BaseModel):
    url: str
    quality: Optional[str] = "best"
    priority: Optional[int] = 0


class BatchDownloadRequest(BaseModel):
    urls: List[str]
    quality: Optional[str] = "best"


class URLInfoRequest(BaseModel):
    url: str


@router.post("")
def create_download(
    payload: CreateDownloadRequest,
    db: Session = Depends(get_db),
):
    if not payload.url or not payload.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")

    job = DownloadJob(
        url=payload.url.strip(),
        quality=payload.quality or "best",
        priority=payload.priority or 0,
        status="pending",
        progress=0.0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Push to Redis queue with priority
    queue.push_job(job.id, priority=job.priority)

    return {"job_id": job.id, "status": "queued", "job": job.to_dict()}


@router.post("/batch")
def create_batch_download(
    payload: BatchDownloadRequest,
    db: Session = Depends(get_db),
):
    if not payload.urls:
        raise HTTPException(status_code=400, detail="URLs required, max 50")
    if len(payload.urls) > 50:
        raise HTTPException(status_code=400, detail="Max 50 URLs per batch")

    jobs = []
    for raw_url in payload.urls:
        cleaned = str(raw_url).strip()
        if not cleaned:
            continue
        job = DownloadJob(
            url=cleaned,
            quality=payload.quality or "best",
            status="pending",
            progress=0.0,
        )
        db.add(job)
        jobs.append(job)

    db.commit()
    for job in jobs:
        db.refresh(job)

    # Push all jobs to Redis queue
    for job in jobs:
        queue.push_job(job.id, priority=job.priority)

    return {
        "message": f"Created {len(jobs)} download jobs",
        "job_ids": [j.id for j in jobs],
    }


@router.get("")
def list_downloads(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(DownloadJob)
    if status:
        query = query.filter_by(status=status)
    jobs = query.order_by(DownloadJob.id.desc()).offset(offset).limit(limit).all()
    return [job.to_dict() for job in jobs]


@router.get("/{job_id}")
def get_download(job_id: int, db: Session = Depends(get_db)):
    job = db.query(DownloadJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    files = db.query(DownloadedFile).filter_by(job_id=job_id).all()
    data = job.to_dict()
    data["files"] = [f.to_dict() for f in files]
    return data


@router.delete("/{job_id}")
def cancel_or_delete_download(job_id: int, db: Session = Depends(get_db)):
    job = db.query(DownloadJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status in ["pending", "processing"]:
        job.status = "cancelled"
        db.commit()
        return {"success": True, "message": "Job cancelled", "job": job.to_dict()}
    else:
        # Delete job and files record
        db.query(DownloadedFile).filter_by(job_id=job_id).delete()
        db.delete(job)
        db.commit()
        return {"success": True, "message": "Job deleted"}


@router.post("/{job_id}/retry")
def retry_download(job_id: int, db: Session = Depends(get_db)):
    job = db.query(DownloadJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "pending"
    job.progress = 0.0
    job.error_message = None
    job.retry_count = (job.retry_count or 0) + 1
    db.commit()
    db.refresh(job)

    # Push to Redis queue for retry
    queue.push_job(job.id, priority=job.priority)

    return {"success": True, "message": "Job queued for retry", "job": job.to_dict()}


def _resolve_info_url(url: Optional[str], payload: Optional[URLInfoRequest]):
    if url:
        return url
    if payload and payload.url:
        return payload.url
    raise HTTPException(status_code=400, detail="URL is required")


@router.post("/info")
def extract_url_info_post(payload: URLInfoRequest):
    target_url = _resolve_info_url(None, payload)
    try:
        info = downloader_service.get_info(target_url)
        if info.get('type') == 'playlist':
            return info
        return {
            "type": "video",
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "extractor": info.get("extractor"),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/info")
def extract_url_info_get(url: str = Query(..., description="Target URL")):
    target_url = _resolve_info_url(url, None)
    try:
        info = downloader_service.get_info(target_url)
        if info.get('type') == 'playlist':
            return info
        return {
            "type": "video",
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "extractor": info.get("extractor"),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
