# AGENTS

Operating contract for AI agents and automation helpers working in this project.

## Mission

- Keep this service lean: FastAPI + uvicorn, src layout; no ORM or DI framework until the app actually needs them.

## Core Rules

- Application code lives under `src/template_app/`; routes in `main.py` (or routers it includes).
- Type hints everywhere; endpoints return typed dicts or pydantic models.
- Every route gets a `TestClient` test under `tests/`.
- Update docs in the same change when behavior or process changes.

## Required Checks Before Finishing

- `pip install -e .[dev]` succeeds.
- `pytest` passes.

## Safe Change Workflow

1. Read the affected files fully before editing.
2. Make the smallest change that solves the task.
3. Run the tests, then review the diff with git before committing.
