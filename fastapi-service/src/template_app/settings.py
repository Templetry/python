"""Settings for TemplateApp, loaded from the active environment profile.

Python has no blessed mechanism for this, so the convention is: one profile
file per environment at the project root, selected by ``APP_ENV``, read
through a single validated object. Nothing else in the codebase should reach
for ``os.environ`` — if a value matters, it belongs here.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "staging", "production"]

# Profiles sit at the project root, next to pyproject.toml. In a container
# there are no files: the platform supplies real environment variables, which
# take priority over any profile anyway.
_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """What the application reads.

    Validated on load, so a profile with a nonsensical value fails at startup
    rather than on the first request that happened to need it.
    """

    model_config = SettingsConfigDict(env_file_encoding="utf-8", extra="ignore")

    environment: Environment = "development"
    log_level: str = "INFO"
    verbose_errors: bool = False
    cache_seconds: int = Field(default=0, ge=0, le=86_400)


@lru_cache
def get_settings(profile: str | None = None) -> Settings:
    """Load a profile by name, or the one ``APP_ENV`` selects.

    ``.env.local`` is layered on top when it exists and is gitignored: the
    place for values that belong to one machine and never to the repository.
    Real environment variables still win over both.
    """
    name = profile or os.getenv("APP_ENV", "development")
    candidates = [_ROOT / f".env.{name}", _ROOT / ".env.local"]
    return Settings(_env_file=[path for path in candidates if path.exists()])
