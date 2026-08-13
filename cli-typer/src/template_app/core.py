"""Library layer: the logic the CLI is a shell over."""


def greeting(name: str) -> str:
    """Build the message the CLI prints."""
    return f"Hello, {name or 'world'}!"
