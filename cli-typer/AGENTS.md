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

## Safe Change Workflow

1. Read the affected files fully before editing.
2. Make the smallest change that solves the task.
3. Run the tests, then review the diff with git before committing.
