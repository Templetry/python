"""TemplateApp application entry point."""

from fastapi import FastAPI

# tpl:if environments
from template_app.settings import get_settings

settings = get_settings()
app = FastAPI(title="TemplateApp", debug=settings.verbose_errors)
# tpl:endif
# tpl:if !environments
app = FastAPI(title="TemplateApp")
# tpl:endif


@app.get("/healthz")
def healthz() -> dict[str, str]:
    # tpl:if environments
    return {"status": "ok", "environment": settings.environment}
    # tpl:endif
    # tpl:if !environments
    return {"status": "ok"}
    # tpl:endif


@app.get("/api/hello/{name}")
def hello(name: str) -> dict[str, str]:
    return {"message": f"Hello, {name}!"}
