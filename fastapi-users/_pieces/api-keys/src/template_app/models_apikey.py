"""API key model for TemplateApp.

The secret is **never stored**: only its hash, plus a short public prefix
used to find the row without hashing every key in the table. The plaintext
exists exactly once, in the response to the creation call.
"""

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class ApiKey(SQLModel, table=True):
    __tablename__ = "api_key"

    id: int | None = Field(default=None, primary_key=True)
    name: str = ""
    prefix: str = Field(index=True, unique=True)  # public lookup handle
    hashed_key: str                               # argon2 hash of the secret
    user_id: int = Field(foreign_key="user.id", index=True)
    scopes: str = ""                              # comma-separated
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used_at: datetime | None = None
    expires_at: datetime | None = None
    revoked_at: datetime | None = None

    @property
    def is_active(self) -> bool:
        now = datetime.now(timezone.utc)
        if self.revoked_at is not None:
            return False
        if self.expires_at is not None and _aware(self.expires_at) <= now:
            return False
        return True

    @property
    def scope_list(self) -> list[str]:
        return [s for s in (self.scopes or "").split(",") if s]


def _aware(value: datetime) -> datetime:
    """SQLite hands back naive datetimes; compare in UTC either way."""
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


class ApiKeyCreate(SQLModel):
    name: str = ""
    scopes: list[str] = []
    expires_in_days: int | None = None


class ApiKeyRead(SQLModel):
    id: int
    name: str
    prefix: str
    scopes: str
    created_at: datetime
    last_used_at: datetime | None
    expires_at: datetime | None
    revoked_at: datetime | None


class ApiKeyCreated(ApiKeyRead):
    """Returned once, at creation. `key` is never retrievable again."""

    key: str
