"""Audit services.

Record an event from anywhere you have a session:

    audit(session, "updated", "invoice", invoice.id, actor=user, detail="status=paid")
"""

from datetime import datetime, timedelta, timezone

from fastapi import Request
from sqlmodel import Session, select

from template_app.models import User
from template_app.models_audit import AuditEntry

# Days of history the cleanup helper keeps; 0 disables pruning entirely.
RETENTION_DAYS = 0  # tpl:var retention_days 0


def audit(
    session: Session,
    action: str,
    object_name: str,
    object_id: object = "",
    *,
    actor: User | None = None,
    detail: str = "",
    request: Request | None = None,
) -> AuditEntry:
    """Append one audit entry. Never raises on missing optional context."""
    entry = AuditEntry(
        action=action,
        object_name=object_name,
        object_id=str(object_id),
        actor_id=getattr(actor, "id", None),
        actor_email=getattr(actor, "email", "") or "",
        detail=detail,
        ip=_client_ip(request),
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def _client_ip(request: Request | None) -> str:
    if request is None:
        return ""
    # Honour the first hop of X-Forwarded-For when behind a proxy.
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""


def recent(
    session: Session,
    *,
    object_name: str | None = None,
    actor_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AuditEntry]:
    stmt = select(AuditEntry).order_by(AuditEntry.id.desc())
    if object_name:
        stmt = stmt.where(AuditEntry.object_name == object_name)
    if actor_id is not None:
        stmt = stmt.where(AuditEntry.actor_id == actor_id)
    return list(session.exec(stmt.offset(offset).limit(limit)).all())


def prune(session: Session) -> int:
    """Delete entries older than RETENTION_DAYS. Returns rows removed.

    Retention is a policy decision: deleting audit history can itself be a
    compliance breach, so the default (0) keeps everything.
    """
    if RETENTION_DAYS <= 0:
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    stale = session.exec(select(AuditEntry).where(AuditEntry.at < cutoff)).all()
    for entry in stale:
        session.delete(entry)
    session.commit()
    return len(stale)
