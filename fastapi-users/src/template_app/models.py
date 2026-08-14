"""Persistence and API models for TemplateApp."""

from datetime import datetime, timezone

from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """A user row. The password hash never leaves this layer."""

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: str = ""
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(SQLModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = ""


class UserRead(SQLModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime


class UserUpdate(SQLModel):
    full_name: str | None = None
    is_active: bool | None = None


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(SQLModel):
    email: EmailStr
    password: str
