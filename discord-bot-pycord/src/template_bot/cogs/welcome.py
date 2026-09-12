import discord
from discord.ext import commands


class Welcome(commands.Cog):
    """Greets new members and optionally assigns an auto-role."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        settings = self.bot.settings  # type: ignore[attr-defined]

        if settings.welcome_channel_id:
            channel = member.guild.get_channel(settings.welcome_channel_id)
            if isinstance(channel, discord.TextChannel):
                await channel.send(f"👋 Welcome to the server, {member.mention}!")

        if settings.auto_role_id:
            role = member.guild.get_role(settings.auto_role_id)
            if role is not None:
                await member.add_roles(role, reason="Auto-role on join")

    @discord.slash_command(name="role", description="Give yourself a role by name")
    async def role(self, ctx: discord.ApplicationContext, role_name: str) -> None:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role is None:
            await ctx.respond(f"No role named '{role_name}' found.", ephemeral=True)
            return
        await ctx.author.add_roles(role, reason="Self-assigned via /role")
        await ctx.respond(f"✅ You now have the **{role.name}** role.", ephemeral=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Welcome(bot))
