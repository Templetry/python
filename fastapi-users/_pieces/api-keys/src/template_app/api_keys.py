"""API key services and the machine-authentication dependency.

Key format: ``<service>_<prefix>_<secret>`` — the prefix is stored in the
clear so lookup is a single indexed query, and only the secret's hash is
persisted. Guard a machine route with:

    @router.get("/things", dependencies=[Depends(require_scope("things:read"))])
"""

import secrets
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlmodel import Session, select

from template_app.deps import SessionDep
from template_app.models import User
from template_app.models_apikey import ApiKey
from template_app.security import hash_password, verify_password

# Prefix identifying keys issued by this service.
SERVICE_PREFIX = "tpl"  # tpl:var key_prefix tpl

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def generate_key(session: Session, user: User, name: str = "", scopes: list[str] | None = None,
                 expires_in_days: int | None = None) -> tuple[ApiKey, str]:
    """Mint a key. Returns the row and the plaintext — show it once."""
    handle = secrets.token_hex(6)
    secret = secrets.token_urlsafe(32)
    plaintext = f"{SERVICE_PREFIX}_{handle}_{secret}"
    row = ApiKey(
        name=name,
        prefix=handle,
        hashed_key=hash_password(secret),
        user_id=user.id,
        scopes=",".join(scopes or []),
        expires_at=(
            datetime.now(timezone.utc) + timedelta(days=expires_in_days)
            if expires_in_days
            else None
        ),
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row, plaintext


def resolve(session: Session, plaintext: str) -> ApiKey | None:
    """Find and verify a presented key, or None."""
    parts = plaintext.split("_")
    if len(parts) != 3 or parts[0] != SERVICE_PREFIX:
        return None
    _, handle, secret = parts
    row = session.exec(select(ApiKey).where(ApiKey.prefix == handle)).first()
    if row is None or not row.is_active:
        return None
    if not verify_password(secret, row.hashed_key):
        return None
    row.last_used_at = datetime.now(timezone.utc)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def revoke(session: Session, row: ApiKey) -> ApiKey:
    if row.revoked_at is None:
        row.revoked_at = datetime.now(timezone.utc)
        session.add(row)
        session.commit()
        session.refresh(row)
    return row


def machine_user(
    session: SessionDep,
    presented: Annotated[str | None, Security(api_key_header)],
) -> User:
    """Authenticate a machine caller by API key."""
    if not presented:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing X-API-Key header")
    row = resolve(session, presented)
    if row is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid, expired or revoked API key")
    user = session.get(User, row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "key owner is gone or inactive")
    return user


MachineUser = Annotated[User, Depends(machine_user)]


def require_scope(scope: str) -> Callable[..., ApiKey]:
    """Dependency enforcing one scope on the presented key."""

    def dependency(
        session: SessionDep,
        presented: Annotated[str | None, Security(api_key_header)],
    ) -> ApiKey:
        if not presented:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing X-API-Key header")
        row = resolve(session, presented)
        if row is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid, expired or revoked API key")
        if scope not in row.scope_list:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"key lacks scope {scope}")
        return row

    return dependency
