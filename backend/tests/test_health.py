from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["service"] == "AgentTrace"
    assert data["status"] == "running"
    assert data["docs"] == "/docs"


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "AgentTrace"


def test_liveness_endpoint() -> None:
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {
        "status": "alive",
    }