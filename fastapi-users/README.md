# TemplateApp

User management API generated with [Templetry](https://github.com/Templetry): FastAPI + SQLModel over SQLite, argon2 password hashing, JWT bearer auth, pytest against an in-memory database.

```sh
pip install -e .[dev]
uvicorn template_app.main:app --reload   # :8000, docs at /docs
pytest
```

## Endpoints

| Method | Path | Auth | What |
|---|---|---|---|
| GET | `/healthz` | — | liveness |
| POST | `/auth/register` | — | create a user |
| POST | `/auth/login` | — | exchange credentials for a bearer token |
| GET | `/users/me` | bearer | the authenticated user |
| GET | `/users` | bearer | list users |
| GET/PATCH/DELETE | `/users/{id}` | bearer | read, update, remove |

Set `SECRET_KEY` and `DATABASE_URL` in the environment before deploying — the defaults are for development only.

## Adding resources

This form ships a **piece per object**: adopt it once per entity and get its model, CRUD router and tests, auto-mounted.

```sh
templetry add crud-resource --set entity=Product
```
