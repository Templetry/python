import time

import discord
from discord.ext import commands


class Utility(commands.Cog):
    """General-purpose commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.slash_command(name="ping", description="Check the bot's latency")
    async def ping(self, ctx: discord.ApplicationContext) -> None:
        await ctx.respond(f"🏓 Pong! {round(self.bot.latency * 1000)}ms")

    @discord.slash_command(name="uptime", description="How long the bot has been running")
    async def uptime(self, ctx: discord.ApplicationContext) -> None:
        seconds = int(time.monotonic() - self.bot.started_at)  # type: ignore[attr-defined]
        await ctx.respond(f"⏱️ Uptime: {seconds // 3600}h {(seconds % 3600) // 60}m {seconds % 60}s")


def setup(bot: commands.Bot) -> None:
    bot.started_at = time.monotonic()  # type: ignore[attr-defined]
    bot.add_cog(Utility(bot))
