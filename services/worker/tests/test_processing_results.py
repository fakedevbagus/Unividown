import json

from fastapi.testclient import TestClient

from app.api.endpoints import tools as tools_endpoint
from app.database import SessionLocal, init_db
from app.main import app
from app.models.processing_job import ProcessingJob
from app.workers.process_worker import recover_interrupted_processing_jobs

init_db()


def create_job(status="completed", output_files=None):
    db = SessionLocal()
    try:
        job = ProcessingJob(
            tool_type="convert",
            status=status,
            progress=100.0 if status == "completed" else 25.0,
            input_files=json.dumps(["/private/upload.mp4"]),
            output_files=json.dumps(output_files or []),
            parameters=json.dumps({"format": "mp4"}),
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job.id
    finally:
        db.close()


def test_processing_job_hides_paths_and_exposes_result_url(tmp_path, monkeypatch):
    result = tmp_path / "result.mp4"
    result.write_bytes(b"processed-media")
    monkeypatch.setattr(tools_endpoint.settings, "processed_dir", str(tmp_path))
    job_id = create_job(output_files=[str(result)])

    with TestClient(app) as client:
        detail = client.get(f"/api/tools/jobs/{job_id}")
        download = client.get(f"/api/tools/jobs/{job_id}/files/0")

    assert detail.status_code == 200
    payload = detail.json()
    assert "input_files" not in payload
    assert "output_files" not in payload
    assert "/private/upload.mp4" not in detail.text
    assert payload["results"][0]["filename"] == "result.mp4"
    assert payload["results"][0]["download_url"].endswith(f"/{job_id}/files/0")
    assert download.status_code == 200
    assert download.content == b"processed-media"


def test_processing_result_rejects_path_outside_root(tmp_path, monkeypatch):
    root = tmp_path / "processed"
    root.mkdir()
    outside = tmp_path / "outside.mp4"
    outside.write_bytes(b"private")
    monkeypatch.setattr(tools_endpoint.settings, "processed_dir", str(root))
    job_id = create_job(output_files=[str(outside)])
    with TestClient(app) as client:
        response = client.get(f"/api/tools/jobs/{job_id}/files/0")
    assert response.status_code == 404


def test_processing_restart_recovery():
    job_id = create_job(status="processing")
    db = SessionLocal()
    try:
        assert recover_interrupted_processing_jobs(db) >= 1
        recovered = db.query(ProcessingJob).filter_by(id=job_id).one()
        assert recovered.status == "pending"
        assert recovered.error_message == "Recovered after worker restart"
    finally:
        db.close()
