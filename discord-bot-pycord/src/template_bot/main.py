import logging

import discord
from discord.ext import commands

from .config import Settings

log = logging.getLogger("bot")

EXTENSIONS = (
    # tpl:if moderation
    "template_bot.cogs.moderation",
    # tpl:endif
    # tpl:if welcome
    "template_bot.cogs.welcome",
    # tpl:endif
    # tpl:if music
    "template_bot.cogs.music",
    # tpl:endif
    "template_bot.cogs.utility",
)


def build_bot(settings: Settings) -> commands.Bot:
    intents = discord.Intents.default()
    intents.message_content = True
    # tpl:if welcome
    intents.members = True
    # tpl:endif

    bot = commands.Bot(command_prefix=settings.prefix, intents=intents)
    bot.settings = settings  # type: ignore[attr-defined]

    for extension in EXTENSIONS:
        bot.load_extension(extension)

    @bot.event
    async def on_ready() -> None:
        log.info("TemplateBot logged in as %s (id=%s)", bot.user, bot.user.id if bot.user else "?")

    return bot


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = Settings.from_env()
    bot = build_bot(settings)
    bot.run(settings.token)


if __name__ == "__main__":
    main()
