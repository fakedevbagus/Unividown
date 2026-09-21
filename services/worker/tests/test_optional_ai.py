import io
from fastapi.testclient import TestClient

import app.api.endpoints.tools as tools_module
from app.main import app


def test_transcription_reports_unavailable_without_ai_profile(monkeypatch):
    monkeypatch.setattr(tools_module.importlib.util, "find_spec", lambda name: None)
    with TestClient(app) as client:
        response = client.post(
            "/api/tools/transcribe",
            files={"file": ("sample.wav", io.BytesIO(b"not audio"), "audio/wav")},
        )
    assert response.status_code == 503
    assert "optional AI profile" in response.json()["detail"]
