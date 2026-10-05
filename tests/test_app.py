from app import app, init_db


def test_health():
    init_db()

    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "OK"
