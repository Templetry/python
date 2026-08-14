"""Persistence and API models for TemplateEntity."""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class TemplateEntity(SQLModel, table=True):
    __tablename__ = "template_entity"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TemplateEntityCreate(SQLModel):
    name: str
    description: str = ""


class TemplateEntityRead(SQLModel):
    id: int
    name: str
    description: str
    created_at: datetime


class TemplateEntityUpdate(SQLModel):
    name: str | None = None
    description: str | None = None
