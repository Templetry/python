from typer.testing import CliRunner

from template_app.cli import app
from template_app.core import greeting

runner = CliRunner()


def test_greeting_defaults_to_world() -> None:
    assert greeting("") == "Hello, world!"


def test_hello_command() -> None:
    result = runner.invoke(app, ["--name", "Python"])
    assert result.exit_code == 0
    assert "Hello, Python!" in result.output
