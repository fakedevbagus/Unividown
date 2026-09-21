import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.endpoints import downloads as downloads_endpoint
from app.database import SessionLocal, init_db
from app.main import app
from app.models.download_job import DownloadJob
from app.models.downloaded_file import DownloadedFile
from app.workers.cancellation import cancellation_registry
from app.workers.download_worker import DownloadWorker, recover_interrupted_downloads

init_db()


def _create_job(status: str = "completed") -> int:
    db = SessionLocal()
    try:
        job = DownloadJob(
            url="https://example.com/lifecycle",
            status=status,
            quality="best",
            progress=100.0 if status == "completed" else 0.0,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job.id
    finally:
        db.close()


def test_result_download_is_contained_and_does_not_leak_path(tmp_path, monkeypatch):
    job_id = _create_job()
    job_dir = tmp_path / str(job_id)
    job_dir.mkdir()
    result = job_dir / "result.mp4"
    result.write_bytes(b"fixture-media")
    monkeypatch.setattr(downloads_endpoint.settings, "download_dir", str(tmp_path))

    db = SessionLocal()
    try:
        file = DownloadedFile(
            job_id=job_id,
            filename=result.name,
            file_path=str(result),
            file_type="video",
            file_size=result.stat().st_size,
        )
        db.add(file)
        db.commit()
        db.refresh(file)
        file_id = file.id
    finally:
        db.close()

    with TestClient(app) as client:
        detail = client.get(f"/api/downloads/{job_id}")
        response = client.get(f"/api/downloads/{job_id}/files/{file_id}")

    assert detail.status_code == 200
    serialized = detail.json()["files"][0]
    assert "file_path" not in serialized
    assert serialized["download_url"].endswith(f"/{job_id}/files/{file_id}")
    assert response.status_code == 200
    assert response.content == b"fixture-media"
    assert 'filename="result.mp4"' in response.headers["content-disposition"]


def test_result_download_rejects_path_outside_job_root(tmp_path, monkeypatch):
    job_id = _create_job()
    outside = tmp_path / "outside.mp4"
    outside.write_bytes(b"must-not-be-served")
    monkeypatch.setattr(downloads_endpoint.settings, "download_dir", str(tmp_path))

    db = SessionLocal()
    try:
        file = DownloadedFile(
            job_id=job_id,
            filename=outside.name,
            file_path=str(outside),
            file_type="video",
            file_size=outside.stat().st_size,
        )
        db.add(file)
        db.commit()
        db.refresh(file)
        file_id = file.id
    finally:
        db.close()

    with TestClient(app) as client:
        response = client.get(f"/api/downloads/{job_id}/files/{file_id}")
    assert response.status_code == 404


def test_processing_cancel_signals_active_worker(monkeypatch):
    job_id = _create_job(status="processing")
    monkeypatch.setattr(downloads_endpoint.queue, "remove_jobs", lambda _ids: True)

    db = SessionLocal()
    try:
        response = downloads_endpoint.cancel_or_delete_download(job_id, db)
    finally:
        db.close()

    assert response["job"]["status"] == "cancelled"
    assert cancellation_registry.is_requested(job_id)
    cancellation_registry.clear(job_id)


def test_restart_recovery_requeues_interrupted_jobs(monkeypatch):
    job_id = _create_job(status="processing")
    removed = []
    pushed = []
    monkeypatch.setattr(
        "app.workers.download_worker.queue.remove_jobs",
        lambda ids: removed.extend(ids) or True,
    )
    monkeypatch.setattr(
        "app.workers.download_worker.queue.push_jobs",
        lambda jobs: pushed.extend(jobs) or True,
    )

    db = SessionLocal()
    try:
        assert recover_interrupted_downloads(db) >= 1
        recovered = db.query(DownloadJob).filter_by(id=job_id).one()
        assert recovered.status == "pending"
        assert recovered.error_message == "Recovered after worker restart"
    finally:
        db.close()

    assert job_id in removed
    assert any(item[0] == job_id for item in pushed)


def test_downloaded_file_is_upserted_on_retry(tmp_path):
    job_id = _create_job(status="processing")
    job_dir = tmp_path / str(job_id)
    job_dir.mkdir()
    result = job_dir / "same-result.mp4"
    result.write_bytes(b"first")

    worker = DownloadWorker()
    worker.downloader.output_dir = Path(tmp_path)
    worker.downloader.download = lambda **_kwargs: {"title": "Fixture"}

    async def run_twice():
        for _ in range(2):
            db = SessionLocal()
            try:
                job = db.query(DownloadJob).filter_by(id=job_id).one()
                job.status = "processing"
                db.commit()
                await worker.download_video(job, db)
            finally:
                db.close()

    asyncio.run(run_twice())

    db = SessionLocal()
    try:
        files = db.query(DownloadedFile).filter_by(job_id=job_id).all()
        assert len(files) == 1
        assert files[0].file_path == str(result.resolve())
    finally:
        db.close()