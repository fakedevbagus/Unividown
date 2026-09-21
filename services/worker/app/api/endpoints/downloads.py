from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.download_job import DownloadJob
from app.models.downloaded_file import DownloadedFile
from app.queue.redis_queue import QueueUnavailable, queue
from app.services.downloader import Downloader
from app.workers.cancellation import cancellation_registry

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


def _resolve_info_url(url: Optional[str], payload: Optional[URLInfoRequest]):
    if url:
        return url
    if payload and payload.url:
        return payload.url
    raise HTTPException(status_code=400, detail="URL is required")


def _format_info(target_url: str):
    try:
        info = downloader_service.get_info(target_url)
        if info.get("type") == "playlist":
            return info
        return {
            "type": "video",
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
            "extractor": info.get("extractor"),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# Static routes must be registered before /{job_id}.
@router.post("/info")
def extract_url_info_post(payload: URLInfoRequest):
    return _format_info(_resolve_info_url(None, payload))


@router.get("/info")
def extract_url_info_get(url: str = Query(..., description="Target URL")):
    return _format_info(_resolve_info_url(url, None))


def _delete_jobs(db: Session, jobs: List[DownloadJob]):
    ids = [job.id for job in jobs if job.id is not None]
    if ids:
        db.query(DownloadJob).filter(DownloadJob.id.in_(ids)).delete(
            synchronize_session=False
        )
        db.commit()


def _serialize_file(file: DownloadedFile):
    return {
        "id": file.id,
        "job_id": file.job_id,
        "filename": file.filename,
        "file_type": file.file_type,
        "file_size": file.file_size,
        "download_url": f"/api/downloads/{file.job_id}/files/{file.id}",
    }


def _serialize_job(db: Session, job: DownloadJob, include_files: bool = False):
    data = job.to_dict()
    if include_files:
        files = db.query(DownloadedFile).filter_by(job_id=job.id).all()
        data["files"] = [_serialize_file(file) for file in files]
    return data


def _enqueue_jobs(db: Session, jobs: List[DownloadJob]) -> bool:
    entries = [(job.id, job.priority or 0) for job in jobs]
    try:
        return queue.push_jobs(entries)
    except QueueUnavailable as exc:
        _delete_jobs(db, jobs)
        raise HTTPException(
            status_code=503,
            detail="Download queue unavailable; no jobs were created",
        ) from exc


@router.post("")
def create_download(payload: CreateDownloadRequest, db: Session = Depends(get_db)):
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

    queued_in_redis = _enqueue_jobs(db, [job])
    return {
        "job_id": job.id,
        "status": "queued",
        "queue_backend": "redis" if queued_in_redis else "database",
        "job": job.to_dict(),
    }


@router.post("/batch")
def create_batch_download(payload: BatchDownloadRequest, db: Session = Depends(get_db)):
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

    if not jobs:
        raise HTTPException(status_code=400, detail="At least one valid URL is required")

    db.commit()
    for job in jobs:
        db.refresh(job)

    queued_in_redis = _enqueue_jobs(db, jobs)
    return {
        "message": f"Created {len(jobs)} download jobs",
        "job_ids": [job.id for job in jobs],
        "queue_backend": "redis" if queued_in_redis else "database",
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
    return [_serialize_job(db, job, include_files=True) for job in jobs]


@router.get("/{job_id}")
def get_download(job_id: int, db: Session = Depends(get_db)):
    job = db.query(DownloadJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return _serialize_job(db, job, include_files=True)


@router.get("/{job_id}/files/{file_id}")
def download_result_file(
    job_id: int, file_id: int, db: Session = Depends(get_db)
):
    file = (
        db.query(DownloadedFile)
        .filter_by(id=file_id, job_id=job_id)
        .first()
    )
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    root = (Path(settings.download_dir).resolve() / str(job_id)).resolve()
    candidate = Path(file.file_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="File not available") from exc

    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="File not available")

    return FileResponse(
        path=candidate,
        filename=file.filename,
        media_type="application/octet-stream",
    )


@router.delete("/{job_id}")
def cancel_or_delete_download(job_id: int, db: Session = Depends(get_db)):
    job = db.query(DownloadJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status in ["pending", "processing"]:
        was_processing = job.status == "processing"
        job.status = "cancelled"
        db.commit()
        if was_processing:
            cancellation_registry.request(job_id)
        else:
            cancellation_registry.clear(job_id)
        try:
            queue.remove_jobs([job_id])
        except QueueUnavailable:
            pass
        return {"success": True, "message": "Job cancelled", "job": job.to_dict()}

    db.query(DownloadedFile).filter_by(job_id=job_id).delete()
    db.delete(job)
    db.commit()
    return {"success": True, "message": "Job deleted"}


@router.post("/{job_id}/retry")
def retry_download(job_id: int, db: Session = Depends(get_db)):
    job = db.query(DownloadJob).filter_by(id=job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status in ["pending", "processing"]:
        return {
            "success": True,
            "message": "Job is already queued or processing",
            "queue_backend": "existing",
            "job": job.to_dict(),
        }

    previous = {
        "status": job.status,
        "progress": job.progress,
        "error_message": job.error_message,
        "retry_count": job.retry_count,
    }
    job.status = "pending"
    job.progress = 0.0
    job.error_message = None
    job.retry_count = (job.retry_count or 0) + 1
    db.commit()
    db.refresh(job)
    cancellation_registry.clear(job_id)

    try:
        queued_in_redis = queue.push_jobs([(job.id, job.priority or 0)])
    except QueueUnavailable as exc:
        job.status = previous["status"]
        job.progress = previous["progress"]
        job.error_message = previous["error_message"]
        job.retry_count = previous["retry_count"]
        db.commit()
        raise HTTPException(status_code=503, detail="Download queue unavailable") from exc

    return {
        "success": True,
        "message": "Job queued for retry",
        "queue_backend": "redis" if queued_in_redis else "database",
        "job": job.to_dict(),
    }
