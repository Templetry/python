# AGENTS

Operating contract for AI agents and automation helpers working in this project.

## Mission

- A user management API: registration, login, and CRUD over users. Keep auth boring and correct.

## Core Rules

- **Never** return `hashed_password` — read models (`UserRead`) exist for that reason.
- Hashing goes through `security.py` (pwdlib/argon2); never roll your own or downgrade the algorithm.
- `SECRET_KEY` comes from the environment; the default is a development placeholder and must fail loudly in production reviews.
- Routers live in `routers/` and are auto-mounted by `main.include_routers` — add a module exposing `router`, never edit `main.py` to register it.
- Every endpoint gets a test using the in-memory database fixtures in `tests/conftest.py`.
- Update docs in the same change when behavior or process changes.

## Required Checks Before Finishing

- `pip install -e .[dev]` succeeds.
- `pytest` passes.

## Safe Change Workflow

1. Read the affected files fully before editing.
2. Make the smallest change that solves the task.
3. Run the tests, then review the diff with git before committing.
