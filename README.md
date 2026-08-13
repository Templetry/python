# Templetry parent: python

Python templates for [Templetry](https://github.com/Templetry). One **parent repo**, multiple **forms** — each form is a subdirectory that compiles on its own and carries its own `template.yml` ([ADR-0011](https://github.com/Templetry/wiki/blob/main/adr/0011-template-forms.md)).

| Form | What it is | Status |
|---|---|---|
| [`fastapi-service/`](fastapi-service/) | FastAPI service — src layout, pytest with TestClient, optional Dockerfile | ✅ ready |
| [`cli-typer/`](cli-typer/) | CLI — Typer commands, src layout, pytest with CliRunner | ✅ ready |

## Usage

```sh
templetry init python/fastapi-service --out ./my-svc --set "project_name=My Service"
```

Forms are **chosen**, not combined. Inside a form, the manifest's features are freely combinable.
