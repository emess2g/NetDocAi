
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_analyze_rejects_missing_config():
    response = client.post("/analyze", json={})
    assert response.status_code == 422


def test_analyze_rejects_non_string_config():
    response = client.post("/analyze", json={"config": 123})
    assert response.status_code == 422


def test_analyze_rejects_empty_config():
    response = client.post("/analyze", json={"config": ""})
    assert response.status_code == 422


def test_analyze_rejects_whitespace_config():
    response = client.post("/analyze", json={"config": "   \n\t"})
    assert response.status_code == 422


def test_analyze_rejects_oversized_config():
    response = client.post(
        "/analyze",
        json={"config": "!" * 1_000_001},
    )
    assert response.status_code == 422


def test_analyze_rejects_nul_character():
    response = client.post(
        "/analyze",
        json={"config": "hostname SW1\x00"},
    )
    assert response.status_code == 422
