import discord
from discord.ext import commands

from .. import storage


class GuildSettings(commands.Cog):
    """Per-guild configuration, persisted to disk so it survives restarts.

    Other cogs (welcome, moderation) read the same storage keys this sets.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    settings_group = discord.SlashCommandGroup("settings", "Configure this bot for your server")

    @settings_group.command(name="welcome_channel", description="Set the channel for welcome messages")
    @commands.has_permissions(manage_guild=True)
    async def welcome_channel(self, ctx: discord.ApplicationContext, channel: discord.TextChannel) -> None:
        storage.set(ctx.guild.id, "welcome_channel_id", channel.id)
        await ctx.respond(f"✅ Welcome messages will be sent in {channel.mention}.", ephemeral=True)

    @settings_group.command(name="auto_role", description="Set the role given to new members")
    @commands.has_permissions(manage_guild=True)
    async def auto_role(self, ctx: discord.ApplicationContext, role: discord.Role) -> None:
        storage.set(ctx.guild.id, "auto_role_id", role.id)
        await ctx.respond(f"✅ New members will get the **{role.name}** role.", ephemeral=True)

    @settings_group.command(name="mod_log", description="Set the channel for moderation logs")
    @commands.has_permissions(manage_guild=True)
    async def mod_log(self, ctx: discord.ApplicationContext, channel: discord.TextChannel) -> None:
        storage.set(ctx.guild.id, "mod_log_channel_id", channel.id)
        await ctx.respond(f"✅ Moderation actions will be logged in {channel.mention}.", ephemeral=True)

    @settings_group.command(name="show", description="Show the current configuration for this server")
    @commands.has_permissions(manage_guild=True)
    async def show(self, ctx: discord.ApplicationContext) -> None:
        guild_settings = storage.all_for_guild(ctx.guild.id)
        if not guild_settings:
            await ctx.respond("No settings configured yet.", ephemeral=True)
            return
        lines = [f"- **{key}**: {value}" for key, value in guild_settings.items()]
        await ctx.respond("\n".join(lines), ephemeral=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(GuildSettings(bot))
