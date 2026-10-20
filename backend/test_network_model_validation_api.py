from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_analyze_returns_network_model_validation():
    response = client.post(
        "/analyze",
        json={
            "config": (
                "hostname R1\n"
                "interface GigabitEthernet0/0\n"
                " ip address 192.168.10.1 255.255.255.0\n"
                " no shutdown\n"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["network_model"], dict)
    assert data["network_model_validation"] == {
        "valid": True,
        "errors": [],
    }
