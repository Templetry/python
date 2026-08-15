"""TemplateApp application entry point."""

import importlib
import pkgutil
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import APIRouter, FastAPI

from template_app import routers
from template_app.db import init_db

# tpl:if environments
from template_app.settings import get_settings

settings = get_settings()
# tpl:endif


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


# tpl:if environments
app = FastAPI(title="TemplateApp", lifespan=lifespan, debug=settings.verbose_errors)
# tpl:endif
# tpl:if !environments
app = FastAPI(title="TemplateApp", lifespan=lifespan)
# tpl:endif


@app.get("/healthz", tags=["meta"])
def healthz() -> dict[str, str]:
    # tpl:if environments
    return {"status": "ok", "environment": settings.environment}
    # tpl:endif
    # tpl:if !environments
    return {"status": "ok"}
    # tpl:endif


def include_routers(application: FastAPI) -> None:
    """Mount every router module found in the routers package.

    This is the piece socket: a piece adds `routers/<name>.py` exposing a
    `router` and it is mounted automatically — no existing file changes.
    """
    for module in pkgutil.iter_modules(routers.__path__):
        mod = importlib.import_module(f"{routers.__name__}.{module.name}")
        candidate = getattr(mod, "router", None)
        if isinstance(candidate, APIRouter):
            application.include_router(candidate)


include_routers(app)
