import logging

import discord
from discord.ext import commands

log = logging.getLogger("bot")


class Admin(commands.Cog):
    """Owner-only maintenance commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.slash_command(name="sync", description="Re-sync slash commands with Discord")
    @commands.is_owner()
    async def sync(self, ctx: discord.ApplicationContext) -> None:
        await self.bot.sync_commands()
        await ctx.respond("🔄 Synced slash commands.", ephemeral=True)

    @discord.slash_command(name="reload", description="Reload a cog by module name (e.g. 'moderation')")
    @commands.is_owner()
    async def reload(self, ctx: discord.ApplicationContext, extension: str) -> None:
        self.bot.reload_extension(f"template_bot.cogs.{extension}")
        await ctx.respond(f"♻️ Reloaded `{extension}`.", ephemeral=True)

    @discord.slash_command(name="shutdown", description="Shut the bot down")
    @commands.is_owner()
    async def shutdown(self, ctx: discord.ApplicationContext) -> None:
        await ctx.respond("👋 Shutting down.", ephemeral=True)
        await self.bot.close()


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Admin(bot))
