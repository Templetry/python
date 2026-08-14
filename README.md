# Templetry parent: python

Python templates for [Templetry](https://github.com/Templetry). One **parent repo**, multiple **forms** — each form is a subdirectory that compiles on its own and carries its own `template.yml` ([ADR-0011](https://github.com/Templetry/wiki/blob/main/adr/0011-template-forms.md)).

| Form | What it is | Status |
|---|---|---|
| [`fastapi-service/`](fastapi-service/) | FastAPI service — src layout, pytest with TestClient, optional Dockerfile | ✅ ready |
| [`cli-typer/`](cli-typer/) | CLI — Typer commands, src layout, pytest with CliRunner | ✅ ready |
| [`fastapi-users/`](fastapi-users/) | User management API — SQLModel/SQLite, argon2 hashing, JWT auth | ✅ ready |

Pieces ([ADR-0014](https://github.com/Templetry/wiki/blob/main/adr/0014-lazy-pieces.md)) live in `_pieces/` and mount themselves through the routers socket, so adopting one edits no existing file:

| Form | Piece | What it adds |
|---|---|---|
| `fastapi-users` | **`rbac`** | Roles, permissions and assignments after the [NIST model](https://github.com/Templetry/wiki/blob/main/study/industrial-pieces-v1.md) (ANSI/INCITS 359-2004), admin endpoints and a `require_permission` dependency |
| `fastapi-users` | **`audit-trail`** | Append-only "who changed what, when, from where", with a read-only query endpoint |
| `fastapi-users` | **`soft-delete`** | `deleted_at` mixin, `alive()`/`deleted()` selects, restore and an explicit purge |
| `fastapi-users` | **`api-keys`** | Machine access: hashed keys with prefix lookup, scopes, expiry, revocation and last-used tracking |
| `fastapi-users` | **`crud-resource`** | A whole entity: model, CRUD router and tests, renamed to your object |

They compose — CI builds an API with all four applied:

```sh
templetry add rbac ./my-api --set admin_role=admin
templetry add audit-trail ./my-api
templetry add soft-delete ./my-api
templetry add crud-resource ./my-api --set entity=Product
```

## Usage

```sh
templetry init python/fastapi-service --out ./my-svc --set "project_name=My Service"
```

Forms are **chosen**, not combined. Inside a form, the manifest's features are freely combinable.
