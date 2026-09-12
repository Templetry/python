import discord
from discord.ext import commands


class Moderation(commands.Cog):
    """Basic moderation: kick, ban, purge."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @discord.slash_command(name="kick", description="Kick a member")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: discord.ApplicationContext, member: discord.Member, reason: str = "No reason given") -> None:
        await member.kick(reason=reason)
        await ctx.respond(f"👢 {member.mention} was kicked. Reason: {reason}")

    @discord.slash_command(name="ban", description="Ban a member")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: discord.ApplicationContext, member: discord.Member, reason: str = "No reason given") -> None:
        await member.ban(reason=reason)
        await ctx.respond(f"🔨 {member.mention} was banned. Reason: {reason}")

    @discord.slash_command(name="purge", description="Delete a number of recent messages")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: discord.ApplicationContext, amount: int = 10) -> None:
        amount = max(1, min(amount, 100))
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.respond(f"🧹 Deleted {len(deleted)} messages.", ephemeral=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Moderation(bot))
