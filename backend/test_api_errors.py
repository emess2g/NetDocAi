
from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_analyze_returns_generic_error_when_analyzer_crashes(monkeypatch):
    def crash(_config):
        raise RuntimeError("sensitive internal implementation detail")

    monkeypatch.setattr(main, "analyze_config", crash)

    response = client.post(
        "/analyze",
        json={"config": "hostname SW1\n"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "An unexpected error occurred while analyzing the configuration."
    )
    assert "sensitive internal implementation detail" not in response.text


def test_analyze_keeps_validation_errors():
    response = client.post("/analyze", json={"config": "   "})

    assert response.status_code == 422
