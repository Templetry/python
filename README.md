# Templetry parent: python

Python templates for [Templetry](https://github.com/Templetry). One **parent repo**, multiple **forms** — each form is a subdirectory that compiles on its own and carries its own `template.yml` ([ADR-0011](https://github.com/Templetry/wiki/blob/main/adr/0011-template-forms.md)).

| Form | What it is | Status |
|---|---|---|
| [`fastapi-service/`](fastapi-service/) | FastAPI service — src layout, pytest with TestClient, optional Dockerfile | ✅ ready |
| [`cli-typer/`](cli-typer/) | CLI — Typer commands, src layout, pytest with CliRunner | ✅ ready |
| [`fastapi-users/`](fastapi-users/) | User management API — SQLModel/SQLite, argon2 hashing, JWT auth | ✅ ready |

Pieces ([ADR-0014](https://github.com/Templetry/wiki/blob/main/adr/0014-lazy-pieces.md)): `fastapi-users` ships **`crud-resource`**, a piece *per object* — adopt it once per entity and it lands the model, the CRUD router and its tests, renamed to your entity and auto-mounted through the routers socket:

```sh
templetry add crud-resource ./my-api --set entity=Product
```

## Usage

```sh
templetry init python/fastapi-service --out ./my-svc --set "project_name=My Service"
```

Forms are **chosen**, not combined. Inside a form, the manifest's features are freely combinable.
