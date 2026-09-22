import io
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.endpoints import tools as tools_endpoint
from app.database import SessionLocal, init_db
from app.main import app
from app.models.processing_job import ProcessingJob
from app.services import uploads

init_db()


def _accept_media(monkeypatch, mime="video/mp4"):
    monkeypatch.setattr(uploads, "detect_mime", lambda _path: mime)


def test_tools_convert_endpoint(tmp_path, monkeypatch):
    _accept_media(monkeypatch)
    monkeypatch.setattr(uploads.settings, "upload_dir", str(tmp_path))
    with TestClient(app) as client:
        response = client.post(
            "/api/tools/convert",
            files={"file": ("sample.mp4", io.BytesIO(b"media"), "video/mp4")},
            data={"format": "mp3"},
        )
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        job_res = client.get(f"/api/tools/jobs/{job_id}")
        assert job_res.status_code == 200
        assert job_res.json()["tool_type"] == "convert"


def test_tools_trim_endpoint(tmp_path, monkeypatch):
    _accept_media(monkeypatch)
    monkeypatch.setattr(uploads.settings, "upload_dir", str(tmp_path))
    with TestClient(app) as client:
        response = client.post(
            "/api/tools/trim",
            files={"file": ("sample.mp4", io.BytesIO(b"media"), "video/mp4")},
            data={"start": 1.0, "end": 5.0},
        )
        assert response.status_code == 200
        assert "job_id" in response.json()


def test_upload_filename_is_uuid_and_contained(tmp_path, monkeypatch):
    _accept_media(monkeypatch)
    monkeypatch.setattr(uploads.settings, "upload_dir", str(tmp_path))
    with TestClient(app) as client:
        response = client.post(
            "/api/tools/convert",
            files={"file": ("../../escape.mp4", io.BytesIO(b"media"), "video/mp4")},
        )
    assert response.status_code == 200
    stored = list(tmp_path.glob("*.mp4"))
    assert len(stored) == 1
    assert stored[0].parent == tmp_path.resolve()
    assert stored[0].name != "escape.mp4"
    assert len(stored[0].stem) == 32


def test_uploads_with_same_name_do_not_overwrite(tmp_path, monkeypatch):
    _accept_media(monkeypatch)
    monkeypatch.setattr(uploads.settings, "upload_dir", str(tmp_path))
    with TestClient(app) as client:
        for content in (b"first", b"second"):
            response = client.post(
                "/api/tools/convert",
                files={"file": ("same.mp4", io.BytesIO(content), "video/mp4")},
            )
            assert response.status_code == 200
    stored = list(tmp_path.glob("*.mp4"))
    assert len(stored) == 2
    assert {path.read_bytes() for path in stored} == {b"first", b"second"}


def test_upload_rejects_unsupported_actual_mime_and_cleans_temp(tmp_path, monkeypatch):
    _accept_media(monkeypatch, "application/x-executable")
    monkeypatch.setattr(uploads.settings, "upload_dir", str(tmp_path))
    with TestClient(app) as client:
        response = client.post(
            "/api/tools/convert",
            files={"file": ("malware.mp4", io.BytesIO(b"not-media"), "video/mp4")},
        )
    assert response.status_code == 415
    assert list(tmp_path.iterdir()) == []


def test_upload_stream_limit_cleans_partial_file(tmp_path, monkeypatch):
    _accept_media(monkeypatch)
    monkeypatch.setattr(uploads.settings, "upload_dir", str(tmp_path))
    monkeypatch.setattr(uploads.settings, "max_file_size", 4)
    with TestClient(app) as client:
        response = client.post(
            "/api/tools/convert",
            files={"file": ("large.mp4", io.BytesIO(b"12345"), "video/mp4")},
        )
    assert response.status_code == 413
    assert list(tmp_path.iterdir()) == []


def test_processing_job_uses_generated_path(tmp_path, monkeypatch):
    _accept_media(monkeypatch)
    monkeypatch.setattr(uploads.settings, "upload_dir", str(tmp_path))
    with TestClient(app) as client:
        response = client.post(
            "/api/tools/convert",
            files={"file": ("named.mp4", io.BytesIO(b"media"), "video/mp4")},
        )
    db = SessionLocal()
    try:
        job = db.query(ProcessingJob).filter_by(id=response.json()["job_id"]).one()
        paths = json.loads(job.input_files)
        assert Path(paths[0]).parent == tmp_path.resolve()
        assert Path(paths[0]).name != "named.mp4"
    finally:
        db.close()
