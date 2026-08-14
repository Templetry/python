"""Runtime configuration for TemplateApp."""

import os

# Secret used to sign access tokens. MUST be overridden in production.
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_TTL_MINUTES: int = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "60"))
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./template-app.db")
