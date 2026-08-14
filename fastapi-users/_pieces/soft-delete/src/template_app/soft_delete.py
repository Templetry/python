"""Soft deletion for TemplateApp.

Deleting a row for real destroys history and orphans foreign keys. This
piece replaces destruction with a `deleted_at` stamp plus filtering that
is **opt-out, not opt-in**: queries built through `alive()` hide deleted
rows, so forgetting the filter is a visible choice rather than a silent
data leak.

Give a model soft deletion by inheriting the mixin:

    class Invoice(SoftDeleteMixin, SQLModel, table=True):
        ...

The mixin composes with other cross-cutting columns (tenant id, audit
stamps) — each contributes its own field and its own filter.
"""

from datetime import datetime, timezone
from typing import TypeVar

from sqlmodel import Field, Session, SQLModel, select
from sqlmodel.sql.expression import SelectOfScalar

T = TypeVar("T", bound="SoftDeleteMixin")


class SoftDeleteMixin(SQLModel):
    """Adds the deletion stamp. `None` means alive."""

    deleted_at: datetime | None = Field(default=None, index=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


def alive(model: type[T]) -> SelectOfScalar[T]:
    """A select that only sees rows which are not deleted."""
    return select(model).where(model.deleted_at == None)  # noqa: E711 — SQL NULL check


def deleted(model: type[T]) -> SelectOfScalar[T]:
    """A select over the deleted rows — the recycle bin."""
    return select(model).where(model.deleted_at != None)  # noqa: E711


def get_alive(session: Session, model: type[T], row_id: int) -> T | None:
    row = session.get(model, row_id)
    if row is None or row.is_deleted:
        return None
    return row


def soft_delete(session: Session, row: T) -> T:
    """Mark a row deleted. Idempotent: re-deleting keeps the first stamp."""
    if row.deleted_at is None:
        row.deleted_at = datetime.now(timezone.utc)
        session.add(row)
        session.commit()
        session.refresh(row)
    return row


def restore(session: Session, row: T) -> T:
    """Bring a soft-deleted row back."""
    if row.deleted_at is not None:
        row.deleted_at = None
        session.add(row)
        session.commit()
        session.refresh(row)
    return row


def purge(session: Session, row: T) -> None:
    """Delete for real. Reserve this for data-retention duties (GDPR
    erasure), never for ordinary application deletes."""
    session.delete(row)
    session.commit()
