"""User management endpoints."""

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from template_app.deps import CurrentUser, SessionDep
from template_app.models import User, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(user: CurrentUser) -> User:
    return user


@router.get("", response_model=list[UserRead])
def list_users(session: SessionDep, _: CurrentUser, limit: int = 50, offset: int = 0) -> list[User]:
    return list(session.exec(select(User).offset(offset).limit(limit)).all())


@router.get("/{user_id}", response_model=UserRead)
def read_user(user_id: int, session: SessionDep, _: CurrentUser) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, session: SessionDep, _: CurrentUser) -> User:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: SessionDep, _: CurrentUser) -> None:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user not found")
    session.delete(user)
    session.commit()
