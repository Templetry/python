"""Role and permission administration endpoints.

Mounted automatically by the routers socket — this piece adds no edits to
existing files (ADR-0014). Every route here requires the admin role.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from template_app.deps import CurrentUser, SessionDep
from template_app.models import User
from template_app.models_rbac import (
    Permission,
    PermissionCreate,
    PermissionRead,
    Role,
    RoleCreate,
    RoleRead,
    UserRole,
)
from template_app.rbac import (
    ADMIN_ROLE,
    assign_role,
    ensure_permission,
    ensure_role,
    grant,
    permissions_of,
    require_role,
    roles_of,
)

router = APIRouter(prefix="/rbac", tags=["rbac"])
admin_only = Depends(require_role(ADMIN_ROLE))


@router.post("/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED,
             dependencies=[admin_only])
def create_role(payload: RoleCreate, session: SessionDep) -> Role:
    if session.exec(select(Role).where(Role.name == payload.name)).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "role already exists")
    return ensure_role(session, payload.name, payload.description)


@router.get("/roles", response_model=list[RoleRead], dependencies=[admin_only])
def list_roles(session: SessionDep) -> list[Role]:
    return list(session.exec(select(Role)).all())


@router.post("/permissions", response_model=PermissionRead,
             status_code=status.HTTP_201_CREATED, dependencies=[admin_only])
def create_permission(payload: PermissionCreate, session: SessionDep) -> Permission:
    return ensure_permission(session, payload.object_name, payload.operation)


@router.get("/permissions", response_model=list[PermissionRead], dependencies=[admin_only])
def list_permissions(session: SessionDep) -> list[Permission]:
    return list(session.exec(select(Permission)).all())


@router.post("/roles/{role_id}/permissions/{permission_id}",
             status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_only])
def grant_permission(role_id: int, permission_id: int, session: SessionDep) -> None:
    role, perm = session.get(Role, role_id), session.get(Permission, permission_id)
    if role is None or perm is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "role or permission not found")
    grant(session, role, perm)


@router.post("/users/{user_id}/roles/{role_id}",
             status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_only])
def assign_user_role(user_id: int, role_id: int, session: SessionDep) -> None:
    user, role = session.get(User, user_id), session.get(Role, role_id)
    if user is None or role is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "user or role not found")
    assign_role(session, user, role)


@router.delete("/users/{user_id}/roles/{role_id}",
               status_code=status.HTTP_204_NO_CONTENT, dependencies=[admin_only])
def revoke_user_role(user_id: int, role_id: int, session: SessionDep) -> None:
    link = session.get(UserRole, (user_id, role_id))
    if link is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "assignment not found")
    session.delete(link)
    session.commit()


@router.get("/me/permissions")
def my_permissions(session: SessionDep, user: CurrentUser) -> dict[str, list[str]]:
    """What the caller may do — handy for driving a UI."""
    return {
        "roles": sorted(r.name for r in roles_of(session, user)),
        "permissions": sorted(permissions_of(session, user)),
    }
