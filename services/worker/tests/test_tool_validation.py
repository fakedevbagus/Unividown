import io

from fastapi.testclient import TestClient

from app.main import app
from app.services import uploads


def post_file(client, endpoint, filename="sample.mp4", data=None):
    return client.post(endpoint, files={"file": (filename, io.BytesIO(b"media"), "application/octet-stream")}, data=data or {})


def test_rejects_invalid_video_format_before_saving(tmp_path, monkeypatch):
    monkeypatch.setattr(uploads.settings, "upload_dir", str(tmp_path))
    with TestClient(app) as client:
        response = post_file(client, "/api/tools/convert", data={"format": "exe"})
    assert response.status_code == 422
    assert list(tmp_path.iterdir()) == []


def test_rejects_invalid_trim_range(tmp_path, monkeypatch):
    monkeypatch.setattr(uploads.settings, "upload_dir", str(tmp_path))
    with TestClient(app) as client:
        response = post_file(client, "/api/tools/trim", data={"start": "10", "end": "5"})
    assert response.status_code == 422
    assert list(tmp_path.iterdir()) == []


def test_image_tool_rejects_video_mime(tmp_path, monkeypatch):
    monkeypatch.setattr(uploads.settings, "upload_dir", str(tmp_path))
    monkeypatch.setattr(uploads, "detect_mime", lambda _path: "video/mp4")
    with TestClient(app) as client:
        response = post_file(client, "/api/tools/image/optimize", filename="spoofed.png")
    assert response.status_code == 415
    assert list(tmp_path.iterdir()) == []


def test_audio_tool_accepts_video_source(tmp_path, monkeypatch):
    monkeypatch.setattr(uploads.settings, "upload_dir", str(tmp_path))
    monkeypatch.setattr(uploads, "detect_mime", lambda _path: "video/mp4")
    with TestClient(app) as client:
        response = post_file(client, "/api/tools/audio/convert", data={"format": "mp3"})
    assert response.status_code == 200


def test_parameter_bounds_are_enforced():
    with TestClient(app) as client:
        image = post_file(client, "/api/tools/image/optimize", filename="sample.png", data={"quality": "101", "max_width": "1920"})
        gif = post_file(client, "/api/tools/gif/make", data={"duration": "31", "fps": "15", "scale": "480"})
    assert image.status_code == 422
    assert gif.status_code == 422


def test_capabilities_report_optional_ai():
    with TestClient(app) as client:
        response = client.get("/api/tools/capabilities")
    assert response.status_code == 200
    payload = response.json()
    assert "mp4" in payload["video_formats"]
    assert "mp3" in payload["audio_formats"]
    assert isinstance(payload["transcription_available"], bool)
