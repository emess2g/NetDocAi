import pytest
from fastapi.testclient import TestClient

from main import app


pytestmark = pytest.mark.requires_auth
client = TestClient(app)


def test_analyze_rejects_missing_bearer_token():
    response = client.post("/analyze", json={"config": "hostname R1"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_syslog_upload_rejects_missing_bearer_token():
    response = client.post(
        "/analyze/upload",
        files={
            "file": (
                "events.log",
                b"2026-10-23T08:58:12Z CAI-RTR-01 %LINK-3-UPDOWN: Interface GigabitEthernet0/0/2, changed state to down\\n",
                "text/plain",
            )
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."
