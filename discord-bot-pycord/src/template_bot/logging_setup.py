import logging


def configure(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # The discord.py/py-cord HTTP layer logs every request at INFO; too noisy by default.
    logging.getLogger("discord.http").setLevel(logging.WARNING)
