from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app, sio_app


def test_liveness_endpoint():
    with TestClient(app) as client:
        response = client.get("/api/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_readiness_healthy(monkeypatch):
    monkeypatch.setattr(main_module, "build_readiness_report", lambda tasks: {
        "status": "ready", "ready": True, "degraded": False, "checks": {}
    })
    with TestClient(app) as client:
        response = client.get("/api/health/ready")
    assert response.status_code == 200
    assert response.json()["ready"] is True


def test_readiness_required_dependency_failure(monkeypatch):
    monkeypatch.setattr(main_module, "build_readiness_report", lambda tasks: {
        "status": "not_ready", "ready": False, "degraded": False,
        "checks": {"redis": {"ok": False, "required": True, "detail": "unavailable"}},
    })
    with TestClient(app) as client:
        response = client.get("/api/health/ready")
    assert response.status_code == 503
    assert response.json()["ready"] is False


def test_metrics_prometheus_format():
    with TestClient(app) as client:
        response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "http_requests_total" in response.text


def test_socketio_polling_handshake():
    with TestClient(sio_app) as client:
        response = client.get("/socket.io/?EIO=4&transport=polling")
    assert response.status_code == 200
    assert response.text.startswith("0{")
    assert '"sid"' in response.text
