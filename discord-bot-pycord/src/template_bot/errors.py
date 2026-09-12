"""Global error handling for slash commands, so every cog gets consistent,
user-facing error messages for free instead of an unhandled traceback.
"""

import logging

import discord
from discord.ext import commands

log = logging.getLogger("bot")


def register(bot: commands.Bot) -> None:
    @bot.event
    async def on_application_command_error(ctx: discord.ApplicationContext, error: discord.DiscordException) -> None:
        error = getattr(error, "original", error)

        if isinstance(error, commands.MissingPermissions):
            message = "You don't have permission to do that."
        elif isinstance(error, commands.CommandOnCooldown):
            message = f"Slow down — try again in {error.retry_after:.1f}s."
        elif isinstance(error, commands.CheckFailure):
            message = "You can't use this command here."
        else:
            log.exception("Unhandled command error in %s", ctx.command, exc_info=error)
            message = "Something went wrong running that command."

        if ctx.response.is_done():
            await ctx.followup.send(message, ephemeral=True)
        else:
            await ctx.respond(message, ephemeral=True)
