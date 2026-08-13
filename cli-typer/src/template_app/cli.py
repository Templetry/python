"""TemplateApp command line interface."""

import typer

from template_app.core import greeting

app = typer.Typer(help="TemplateApp command line tool.")


@app.command()
def hello(name: str = typer.Option("world", "--name", "-n", help="Who to greet")) -> None:
    """Print a greeting."""
    typer.echo(greeting(name))


if __name__ == "__main__":
    app()
