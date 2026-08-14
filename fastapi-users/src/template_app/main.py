"""TemplateApp application entry point."""

import importlib
import pkgutil
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import APIRouter, FastAPI

from template_app import routers
from template_app.db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_db()
    yield


app = FastAPI(title="TemplateApp", lifespan=lifespan)


@app.get("/healthz", tags=["meta"])
def healthz() -> dict[str, str]:
    return {"status": "ok"}


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
