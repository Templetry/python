import discord
from discord.ext import commands

from .. import storage


class CustomCommands(commands.Cog):
    """Lets server admins define simple text-response commands at runtime."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.slash_command(name="addcommand", description="Add a custom text command")
    @commands.has_permissions(manage_guild=True)
    async def add_command(self, ctx: discord.ApplicationContext, name: str, response: str) -> None:
        commands_map = storage.get(ctx.guild.id, "custom_commands", {})
        commands_map[name.lower()] = response
        storage.set(ctx.guild.id, "custom_commands", commands_map)
        await ctx.respond(f"✅ Added `/say {name}`.", ephemeral=True)

    @discord.slash_command(name="removecommand", description="Remove a custom text command")
    @commands.has_permissions(manage_guild=True)
    async def remove_command(self, ctx: discord.ApplicationContext, name: str) -> None:
        commands_map = storage.get(ctx.guild.id, "custom_commands", {})
        removed = commands_map.pop(name.lower(), None)
        storage.set(ctx.guild.id, "custom_commands", commands_map)
        await ctx.respond("🗑️ Removed." if removed else "No such command.", ephemeral=True)

    @discord.slash_command(name="say", description="Trigger a custom command by name")
    async def say(self, ctx: discord.ApplicationContext, name: str) -> None:
        commands_map = storage.get(ctx.guild.id, "custom_commands", {})
        response = commands_map.get(name.lower())
        if response is None:
            await ctx.respond("No such command.", ephemeral=True)
            return
        await ctx.respond(response)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(CustomCommands(bot))
