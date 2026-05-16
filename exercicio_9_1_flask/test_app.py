from app import app


def test_health():
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_create_task():
    client = app.test_client()
    response = client.post(
        "/api/tasks",
        json={"title": "Teste automatizado", "description": "Criada pelo pytest"},
    )
    assert response.status_code == 201
    assert response.get_json()["title"] == "Teste automatizado"
