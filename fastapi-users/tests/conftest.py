import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from template_app.db import get_session
from template_app.main import app


@pytest.fixture(name="client")
def client_fixture():
    """A client backed by a throwaway in-memory database."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    def session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = session_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(name="auth")
def auth_fixture(client):
    """Register a user and return its Authorization header."""
    client.post(
        "/auth/register",
        json={"email": "a@example.com", "password": "sup3rsecret", "full_name": "Ada"},
    )
    res = client.post("/auth/login", json={"email": "a@example.com", "password": "sup3rsecret"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}
