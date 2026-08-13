from fastapi.testclient import TestClient

from template_app.main import app

client = TestClient(app)


def test_healthz() -> None:
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_hello() -> None:
    res = client.get("/api/hello/Python")
    assert res.status_code == 200
    assert res.json() == {"message": "Hello, Python!"}
