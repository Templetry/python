"""TemplateApp command line interface."""

import typer

from template_app.core import greeting

# tpl:if environments
from template_app.settings import get_settings
# tpl:endif

app = typer.Typer(help="TemplateApp command line tool.")


@app.command()
def hello(name: str = typer.Option("world", "--name", "-n", help="Who to greet")) -> None:
    """Print a greeting."""
    # tpl:if environments
    settings = get_settings()
    if settings.verbose_errors:
        # Diagnostics go to stderr so piping the output stays clean.
        typer.echo(f"[{settings.environment}] log level {settings.log_level}", err=True)
    # tpl:endif
    typer.echo(greeting(name))


if __name__ == "__main__":
    app()
