import pytest
from sqlmodel import select

from template_app.audit import audit, prune, recent
from template_app.db import get_session
from template_app.main import app
from template_app.models import User


@pytest.fixture(name="session")
def session_fixture(client):
    generator = app.dependency_overrides[get_session]()
    session = next(generator)
    yield session
    generator.close()


def test_audit_records_and_queries(client, auth, session) -> None:
    user = session.exec(select(User).where(User.email == "a@example.com")).one()

    audit(session, "updated", "invoice", 7, actor=user, detail="status=paid")
    audit(session, "deleted", "invoice", 8, actor=user)
    audit(session, "login", "user", user.id, actor=user)

    assert len(recent(session)) == 3
    invoices = recent(session, object_name="invoice")
    assert len(invoices) == 2
    assert invoices[0].object_id == "8"  # newest first
    assert invoices[1].detail == "status=paid"
    assert invoices[1].actor_email == "a@example.com"


def test_audit_endpoint_filters(client, auth, session) -> None:
    user = session.exec(select(User).where(User.email == "a@example.com")).one()
    audit(session, "created", "invoice", 1, actor=user)
    audit(session, "created", "product", 2, actor=user)

    assert client.get("/audit").status_code == 401

    body = client.get("/audit", headers=auth).json()
    assert len(body) == 2

    filtered = client.get("/audit?object_name=product", headers=auth).json()
    assert len(filtered) == 1 and filtered[0]["object_name"] == "product"


def test_audit_is_append_only_over_http(client, auth) -> None:
    # No write routes exist: the trail cannot be rewritten through the API.
    assert client.post("/audit", json={}, headers=auth).status_code == 405
    assert client.delete("/audit", headers=auth).status_code == 405


def test_prune_keeps_everything_by_default(client, auth, session) -> None:
    user = session.exec(select(User).where(User.email == "a@example.com")).one()
    audit(session, "created", "invoice", 1, actor=user)
    assert prune(session) == 0
    assert len(recent(session)) == 1
