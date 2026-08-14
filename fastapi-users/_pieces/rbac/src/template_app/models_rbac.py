"""RBAC model for TemplateApp.

Follows the NIST RBAC reference model (ANSI/INCITS 359-2004): users are
assigned ROLES, roles hold PERMISSIONS, and a permission is an approval to
perform an OPERATION on an OBJECT. Permissions are therefore stored as the
pair (object, operation) and rendered as "object:operation".
"""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Role(SQLModel, table=True):
    """A job function. Users get roles, never permissions directly."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Permission(SQLModel, table=True):
    """An approval to perform `operation` on `object_name`."""

    id: int | None = Field(default=None, primary_key=True)
    object_name: str = Field(index=True)
    operation: str = Field(index=True)
    description: str = ""

    @property
    def code(self) -> str:
        return f"{self.object_name}:{self.operation}"


class RolePermission(SQLModel, table=True):
    """Permission assignment (PA in the NIST model)."""

    role_id: int = Field(foreign_key="role.id", primary_key=True)
    permission_id: int = Field(foreign_key="permission.id", primary_key=True)


class UserRole(SQLModel, table=True):
    """User assignment (UA in the NIST model)."""

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)


class RoleCreate(SQLModel):
    name: str
    description: str = ""


class RoleRead(SQLModel):
    id: int
    name: str
    description: str


class PermissionCreate(SQLModel):
    object_name: str
    operation: str
    description: str = ""


class PermissionRead(SQLModel):
    id: int
    object_name: str
    operation: str
    description: str
