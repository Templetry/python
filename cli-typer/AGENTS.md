# AGENTS

Operating contract for AI agents and automation helpers working in this project.

## Mission

- Keep the split honest: logic in `core.py` (importable, testable), argument parsing in `cli.py`.

## Core Rules

- Commands are Typer functions with typed parameters and a docstring (it becomes the help text).
- Type hints everywhere; no logic in the command bodies beyond calling the library and echoing.
- Every command gets a `CliRunner` test; every core function gets a direct test.
- Update docs in the same change when behavior or process changes.

## Required Checks Before Finishing

- `pip install -e .[dev]` succeeds.
- `pytest` passes.

```sh templetry:checks
pip install -e .[dev]
pytest
```

## Safe Change Workflow

1. Read the affected files fully before editing.
2. Make the smallest change that solves the task.
3. Run the tests, then review the diff with git before committing.

## This project came from a template

Four facts you cannot infer from the code in front of you:

- **Never hand-edit `.templetry-answers.yml`.** It records what generated this project. Editing it makes the next update merge against a state that never existed.
- **Before writing a capability by hand, run `templetry pieces`.** Auth, RBAC, audit trails, API keys and whole CRUD resources may already exist as pieces for this template. Adopting one is `templetry add <name>`, and it brings its own tests.
- **`templetry update` pulls improvements from the template** through a three-way merge that keeps your edits. Use it instead of copying files from the template by hand.
- **Directives like `tpl:if` belong to the template, not here.** If you find one in this project, it is a rendering bug worth reporting — do not try to interpret it.
