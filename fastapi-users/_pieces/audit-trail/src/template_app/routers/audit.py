"""Audit query endpoints — read-only by design.

Mounted through the routers socket. There is deliberately no way to create
or delete entries over HTTP: an audit trail an API can rewrite is not one.
"""

from fastapi import APIRouter

from template_app.audit import recent
from template_app.deps import CurrentUser, SessionDep
from template_app.models_audit import AuditEntryRead

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditEntryRead])
def list_entries(
    session: SessionDep,
    _: CurrentUser,
    object_name: str | None = None,
    actor_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AuditEntryRead]:
    return recent(
        session, object_name=object_name, actor_id=actor_id, limit=limit, offset=offset
    )
