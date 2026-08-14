"""Audit model for TemplateApp.

An audit entry is **append-only**: never updated, never deleted by the
application. It answers the compliance question "who changed what, when,
and from where" — the record an auditor asks for.
"""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class AuditEntry(SQLModel, table=True):
    __tablename__ = "audit_entry"

    id: int | None = Field(default=None, primary_key=True)
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    actor_id: int | None = Field(default=None, index=True)
    actor_email: str = ""
    action: str = Field(index=True)      # created | updated | deleted | login | custom
    object_name: str = Field(index=True) # the entity type, e.g. "user"
    object_id: str = ""                  # the entity key, as text (ids are not all ints)
    detail: str = ""                     # short human-readable summary
    ip: str = ""


class AuditEntryRead(SQLModel):
    id: int
    at: datetime
    actor_id: int | None
    actor_email: str
    action: str
    object_name: str
    object_id: str
    detail: str
    ip: str
