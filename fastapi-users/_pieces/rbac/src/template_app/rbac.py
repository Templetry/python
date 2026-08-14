"""RBAC services and the permission dependency.

Guard a route with:

    @router.get("/things", dependencies=[Depends(require_permission("thing:read"))])
"""

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from template_app.deps import CurrentUser, SessionDep
from template_app.models import User
from template_app.models_rbac import Permission, Role, RolePermission, UserRole

# Role that is granted every permission on bootstrap.
ADMIN_ROLE = "admin"  # tpl:var admin_role admin


def ensure_role(session: Session, name: str, description: str = "") -> Role:
    role = session.exec(select(Role).where(Role.name == name)).first()
    if role is None:
        role = Role(name=name, description=description)
        session.add(role)
        session.commit()
        session.refresh(role)
    return role


def ensure_permission(session: Session, object_name: str, operation: str) -> Permission:
    stmt = select(Permission).where(
        Permission.object_name == object_name, Permission.operation == operation
    )
    perm = session.exec(stmt).first()
    if perm is None:
        perm = Permission(object_name=object_name, operation=operation)
        session.add(perm)
        session.commit()
        session.refresh(perm)
    return perm


def grant(session: Session, role: Role, perm: Permission) -> None:
    """Assign a permission to a role (idempotent)."""
    existing = session.get(RolePermission, (role.id, perm.id))
    if existing is None:
        session.add(RolePermission(role_id=role.id, permission_id=perm.id))
        session.commit()


def assign_role(session: Session, user: User, role: Role) -> None:
    """Assign a role to a user (idempotent)."""
    existing = session.get(UserRole, (user.id, role.id))
    if existing is None:
        session.add(UserRole(user_id=user.id, role_id=role.id))
        session.commit()


def roles_of(session: Session, user: User) -> list[Role]:
    stmt = select(Role).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user.id)
    return list(session.exec(stmt).all())


def permissions_of(session: Session, user: User) -> set[str]:
    """Every permission code the user holds through their roles."""
    stmt = (
        select(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(UserRole, UserRole.role_id == RolePermission.role_id)
        .where(UserRole.user_id == user.id)
    )
    return {p.code for p in session.exec(stmt).all()}


def has_permission(session: Session, user: User, code: str) -> bool:
    return code in permissions_of(session, user)


def require_permission(code: str) -> Callable[..., User]:
    """FastAPI dependency enforcing one permission code."""

    def dependency(session: SessionDep, user: CurrentUser) -> User:
        if not has_permission(session, user, code):
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"missing permission {code}")
        return user

    return dependency


def require_role(name: str) -> Callable[..., User]:
    """FastAPI dependency enforcing membership of one role."""

    def dependency(session: SessionDep, user: CurrentUser) -> User:
        if name not in {r.name for r in roles_of(session, user)}:
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"missing role {name}")
        return user

    return dependency


AdminUser = Depends(require_role(ADMIN_ROLE))
