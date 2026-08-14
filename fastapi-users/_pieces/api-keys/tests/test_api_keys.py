import pytest
from sqlmodel import select

from template_app.api_keys import SERVICE_PREFIX, machine_user, resolve
from template_app.db import get_session
from template_app.main import app
from template_app.models import User
from template_app.models_apikey import ApiKey


@pytest.fixture(name="session")
def session_fixture(client):
    generator = app.dependency_overrides[get_session]()
    session = next(generator)
    yield session
    generator.close()


def test_key_is_returned_once_and_stored_hashed(client, auth, session) -> None:
    created = client.post(
        "/api-keys", json={"name": "ci", "scopes": ["things:read"]}, headers=auth
    )
    assert created.status_code == 201
    body = created.json()
    plaintext = body["key"]
    assert plaintext.startswith(f"{SERVICE_PREFIX}_")

    # Listing never exposes the secret again.
    listed = client.get("/api-keys", headers=auth).json()
    assert len(listed) == 1 and "key" not in listed[0]

    row = session.exec(select(ApiKey)).one()
    assert row.hashed_key != plaintext
    assert plaintext.split("_")[2] not in row.hashed_key


def test_key_authenticates_and_tracks_use(client, auth, session) -> None:
    plaintext = client.post("/api-keys", json={"name": "ci"}, headers=auth).json()["key"]

    row = resolve(session, plaintext)
    assert row is not None and row.last_used_at is not None

    assert resolve(session, f"{SERVICE_PREFIX}_deadbeef_wrong") is None
    assert resolve(session, "nonsense") is None


def test_revoked_key_stops_working(client, auth, session) -> None:
    created = client.post("/api-keys", json={"name": "ci"}, headers=auth).json()
    plaintext = created["key"]
    assert resolve(session, plaintext) is not None

    assert client.delete(f"/api-keys/{created['id']}", headers=auth).status_code == 204
    assert resolve(session, plaintext) is None


def test_expired_key_stops_working(client, auth, session) -> None:
    from datetime import datetime, timedelta, timezone

    plaintext = client.post("/api-keys", json={"name": "ci"}, headers=auth).json()["key"]
    row = session.exec(select(ApiKey)).one()
    row.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    session.add(row)
    session.commit()

    assert resolve(session, plaintext) is None


def test_machine_user_resolves_the_owner(client, auth, session) -> None:
    plaintext = client.post("/api-keys", json={"name": "ci"}, headers=auth).json()["key"]
    user = machine_user(session, plaintext)
    assert isinstance(user, User) and user.email == "a@example.com"


def test_secret_may_contain_underscores(client, auth, session) -> None:
    """Regression: token_urlsafe emits base64url, whose alphabet includes
    '_'. Parsing must split the key at most twice or such keys never
    authenticate — a failure that only shows up on some generated keys."""
    from template_app.api_keys import generate_key
    from template_app.security import hash_password

    user = session.exec(select(User).where(User.email == "a@example.com")).one()
    row, _ = generate_key(session, user, "underscored")
    secret = "abc_def_ghi"
    row.hashed_key = hash_password(secret)
    session.add(row)
    session.commit()

    assert resolve(session, f"{SERVICE_PREFIX}_{row.prefix}_{secret}") is not None


def test_keys_are_private_to_their_owner(client, auth, session) -> None:
    created = client.post("/api-keys", json={"name": "mine"}, headers=auth).json()

    client.post(
        "/auth/register", json={"email": "b@example.com", "password": "sup3rsecret"}
    )
    token = client.post(
        "/auth/login", json={"email": "b@example.com", "password": "sup3rsecret"}
    ).json()["access_token"]
    other = {"Authorization": f"Bearer {token}"}

    assert client.get("/api-keys", headers=other).json() == []
    assert client.delete(f"/api-keys/{created['id']}", headers=other).status_code == 404
