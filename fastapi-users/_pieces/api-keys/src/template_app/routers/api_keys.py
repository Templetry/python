"""API key management — the human owner administers their machine keys."""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from template_app.api_keys import generate_key, revoke
from template_app.deps import CurrentUser, SessionDep
from template_app.models_apikey import ApiKey, ApiKeyCreate, ApiKeyCreated, ApiKeyRead

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("", response_model=ApiKeyCreated, status_code=status.HTTP_201_CREATED)
def create_key(payload: ApiKeyCreate, session: SessionDep, user: CurrentUser) -> ApiKeyCreated:
    row, plaintext = generate_key(
        session, user, payload.name, payload.scopes, payload.expires_in_days
    )
    # The only moment the plaintext exists outside the caller's hands.
    return ApiKeyCreated(**row.model_dump(), key=plaintext)


@router.get("", response_model=list[ApiKeyRead])
def list_keys(session: SessionDep, user: CurrentUser) -> list[ApiKey]:
    return list(session.exec(select(ApiKey).where(ApiKey.user_id == user.id)).all())


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_key(key_id: int, session: SessionDep, user: CurrentUser) -> None:
    row = session.get(ApiKey, key_id)
    if row is None or row.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "key not found")
    revoke(session, row)
