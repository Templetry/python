"""TemplateApp application entry point."""

from fastapi import FastAPI

app = FastAPI(title="TemplateApp")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/hello/{name}")
def hello(name: str) -> dict[str, str]:
    return {"message": f"Hello, {name}!"}
