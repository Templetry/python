"""RBAC tests: the NIST triangle (user → role → permission) end to end."""

import pytest
from sqlmodel import Session, select

from template_app.db import get_session
from template_app.main import app
from template_app.models import User
from template_app.rbac import (
    ADMIN_ROLE,
    assign_role,
    ensure_permission,
    ensure_role,
    grant,
    has_permission,
    permissions_of,
)


@pytest.fixture(name="session")
def session_fixture(client):
    """A session on the same database the app uses under test."""
    generator = app.dependency_overrides[get_session]()
    session = next(generator)
    yield session
    generator.close()


def make_admin(session: Session, email: str = "a@example.com") -> User:
    user = session.exec(select(User).where(User.email == email)).one()
    role = ensure_role(session, ADMIN_ROLE, "bootstrap")
    assign_role(session, user, role)
    return user


def test_permission_flow_without_http(client, auth, session) -> None:
    user = session.exec(select(User).where(User.email == "a@example.com")).one()
    assert permissions_of(session, user) == set()

    role = ensure_role(session, "editor")
    perm = ensure_permission(session, "article", "write")
    grant(session, role, perm)
    assign_role(session, user, role)

    assert has_permission(session, user, "article:write")
    assert not has_permission(session, user, "article:delete")


def test_admin_routes_are_guarded(client, auth, session) -> None:
    # A plain user may not administer roles.
    assert client.get("/rbac/roles", headers=auth).status_code == 403

    make_admin(session)
    assert client.get("/rbac/roles", headers=auth).status_code == 200


def test_role_and_permission_administration(client, auth, session) -> None:
    make_admin(session)

    role = client.post("/rbac/roles", json={"name": "editor"}, headers=auth)
    assert role.status_code == 201
    role_id = role.json()["id"]
    assert client.post("/rbac/roles", json={"name": "editor"}, headers=auth).status_code == 409

    perm = client.post(
        "/rbac/permissions", json={"object_name": "article", "operation": "write"}, headers=auth
    )
    assert perm.status_code == 201
    perm_id = perm.json()["id"]

    assert client.post(
        f"/rbac/roles/{role_id}/permissions/{perm_id}", headers=auth
    ).status_code == 204

    user_id = client.get("/users/me", headers=auth).json()["id"]
    assert client.post(f"/rbac/users/{user_id}/roles/{role_id}", headers=auth).status_code == 204

    mine = client.get("/rbac/me/permissions", headers=auth).json()
    assert "article:write" in mine["permissions"]
    assert "editor" in mine["roles"]

    assert client.delete(f"/rbac/users/{user_id}/roles/{role_id}", headers=auth).status_code == 204
    mine = client.get("/rbac/me/permissions", headers=auth).json()
    assert "article:write" not in mine["permissions"]


def test_missing_entities_return_404(client, auth, session) -> None:
    make_admin(session)
    assert client.post("/rbac/roles/999/permissions/999", headers=auth).status_code == 404
    assert client.post("/rbac/users/999/roles/999", headers=auth).status_code == 404
