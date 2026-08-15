"""Verifactu registry endpoints — read-only, like any legal record.

There is deliberately no route that creates, edits or deletes a record:
records are appended by the invoicing code through
`verifactu.register_invoice`, and the chain is what makes them evidence.
"""

from fastapi import APIRouter
from sqlmodel import select

from template_app.deps import CurrentUser, SessionDep
from template_app.models_verifactu import (
    EventRecord,
    EventRecordRead,
    InvoiceRecord,
    InvoiceRecordRead,
)
from template_app.verifactu import verify_chain

router = APIRouter(prefix="/verifactu", tags=["verifactu"])


@router.get("/records", response_model=list[InvoiceRecordRead])
def list_records(session: SessionDep, _: CurrentUser, limit: int = 100, offset: int = 0):
    stmt = select(InvoiceRecord).order_by(InvoiceRecord.id.desc()).offset(offset).limit(limit)
    return list(session.exec(stmt).all())


@router.get("/events", response_model=list[EventRecordRead])
def list_events(session: SessionDep, _: CurrentUser, limit: int = 100, offset: int = 0):
    stmt = select(EventRecord).order_by(EventRecord.id.desc()).offset(offset).limit(limit)
    return list(session.exec(stmt).all())


@router.get("/verify")
def verify(session: SessionDep, _: CurrentUser) -> dict[str, object]:
    """Re-compute the whole chain. `broken` must always be empty."""
    broken = verify_chain(session)
    return {"ok": not broken, "broken": broken}
