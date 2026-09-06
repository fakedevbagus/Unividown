from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

# Ensure tables are initialized for testing
init_db()


def test_status_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["service"] == "unividown-worker"


def test_create_and_list_downloads():
    with TestClient(app) as client:
        # Create job
        create_res = client.post("/api/downloads", json={"url": "https://example.com/video", "quality": "720"})
        assert create_res.status_code == 200
        res_json = create_res.json()
        assert "job_id" in res_json
        job_id = res_json["job_id"]

        # Get job
        get_res = client.get(f"/api/downloads/{job_id}")
        assert get_res.status_code == 200
        assert get_res.json()["url"] == "https://example.com/video"

        # List jobs
        list_res = client.get("/api/downloads")
        assert list_res.status_code == 200
        assert any(j["id"] == job_id for j in list_res.json())

        # Cancel/delete job
        del_res = client.delete(f"/api/downloads/{job_id}")
        assert del_res.status_code == 200

