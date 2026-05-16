from app import app


def test_health():
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["cloud"] == "Render"


def test_tasks_list():
    client = app.test_client()
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
