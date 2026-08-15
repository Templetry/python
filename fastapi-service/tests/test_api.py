from fastapi.testclient import TestClient

from template_app.main import app

client = TestClient(app)


def test_healthz() -> None:
    res = client.get("/healthz")
    assert res.status_code == 200
    # The status is the contract; the payload may carry more (the active
    # environment, a build id) without that being a breaking change.
    assert res.json()["status"] == "ok"


def test_hello() -> None:
    res = client.get("/api/hello/Python")
    assert res.status_code == 200
    assert res.json() == {"message": "Hello, Python!"}
