from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_task():
    response = client.post(
        "/api/tasks",
        json={"title": "Teste FastAPI", "description": "Criada pelo pytest"},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Teste FastAPI"
