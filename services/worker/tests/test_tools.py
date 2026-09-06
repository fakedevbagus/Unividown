import io
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()


def test_tools_convert_endpoint():
    with TestClient(app) as client:
        dummy_file = io.BytesIO(b"fake media content")
        files = {"file": ("sample.mp4", dummy_file, "video/mp4")}
        response = client.post("/api/tools/convert", files=files, data={"format": "mp3"})
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "queued"

        # Check job list
        job_id = data["job_id"]
        job_res = client.get(f"/api/tools/jobs/{job_id}")
        assert job_res.status_code == 200
        assert job_res.json()["tool_type"] == "convert"


def test_tools_trim_endpoint():
    with TestClient(app) as client:
        dummy_file = io.BytesIO(b"fake media content for trim")
        files = {"file": ("sample.mp4", dummy_file, "video/mp4")}
        response = client.post("/api/tools/trim", files=files, data={"start": 1.0, "end": 5.0})
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
