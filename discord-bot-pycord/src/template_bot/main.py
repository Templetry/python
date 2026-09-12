import logging
import pkgutil

import discord
from discord.ext import commands

from . import cogs
from .config import Settings
from .errors import register as register_error_handlers
from .logging_setup import configure

log = logging.getLogger("bot")


def _discover_extensions() -> list[str]:
    """Every module under `cogs/` is loaded automatically.

    A feature that's off never has its cog file rendered here in the first
    place (see template.yml's `features[].files`), so this needs no
    conditional logic — drop a new cog in and it's wired up for free.
    """
    return [f"{cogs.__name__}.{module.name}" for module in pkgutil.iter_modules(cogs.__path__)]


def build_bot(settings: Settings) -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix=settings.prefix, intents=intents)
    bot.settings = settings  # type: ignore[attr-defined]

    for extension in _discover_extensions():
        bot.load_extension(extension)

    register_error_handlers(bot)

    @bot.event
    async def on_ready() -> None:
        log.info("TemplateBot logged in as %s (id=%s)", bot.user, bot.user.id if bot.user else "?")

    return bot


def main() -> None:
    configure()
    settings = Settings.from_env()
    bot = build_bot(settings)
    bot.run(settings.token)


if __name__ == "__main__":
    main()
