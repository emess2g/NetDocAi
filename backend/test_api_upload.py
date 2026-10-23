from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def upload(filename, content):
    return client.post(
        "/analyze/upload",
        files={"file": (filename, content, "text/plain")},
    )


def test_upload_valid_config():
    response = upload(
        "switch.cfg",
        b"hostname SW1\n",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["hostname"] == "SW1"
    assert "findings" in data
    assert "health" in data
    assert "summary" in data


def test_upload_accepts_supported_extensions():
    for filename in ("switch.cfg", "switch.conf", "switch.txt", "switch.log"):
        response = upload(filename, b"hostname SW1\n")
        assert response.status_code == 200, filename


def test_upload_rejects_unsupported_extension():
    response = upload("switch.pdf", b"hostname SW1\n")

    assert response.status_code == 400


def test_upload_rejects_empty_file():
    response = upload("switch.cfg", b"")

    assert response.status_code == 400


def test_upload_rejects_whitespace_only_file():
    response = upload("switch.cfg", b"   \n\t")

    assert response.status_code == 400


def test_upload_rejects_oversized_file():
    response = upload("switch.cfg", b"A" * 1_000_001)

    assert response.status_code == 413


def test_upload_rejects_nul_character():
    response = upload("switch.cfg", b"hostname SW1\x00\n")

    assert response.status_code == 400


def test_upload_rejects_invalid_utf8():
    response = upload("switch.cfg", b"\xff\xfe\xfa")

    assert response.status_code == 400


def test_upload_without_filename_is_rejected():
    response = client.post(
        "/analyze/upload",
        files={"file": (None, b"hostname SW1\n", "text/plain")},
    )

    assert response.status_code == 422


def test_upload_accepts_file_at_exact_size_limit():
    prefix = b"hostname SW1\n"
    content = prefix + b"!" * (1_000_000 - len(prefix))

    response = upload("switch.cfg", content)

    assert response.status_code == 200
    assert response.json()["hostname"] == "SW1"


def test_upload_returns_generic_error_when_analyzer_crashes(monkeypatch):
    import main

    def crash(_config):
        raise RuntimeError("sensitive internal implementation detail")

    monkeypatch.setattr(main, "analyze_config", crash)

    response = upload("switch.cfg", b"hostname SW1\n")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "An unexpected error occurred while analyzing the configuration."
    )
    assert "sensitive internal implementation detail" not in response.text
