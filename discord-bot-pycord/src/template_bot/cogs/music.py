import asyncio

import discord
from discord.ext import commands
from yt_dlp import YoutubeDL

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch",
}
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


class Music(commands.Cog):
    """Plays audio in a voice channel from a search query or URL."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._ytdl = YoutubeDL(YTDL_OPTIONS)

    @discord.slash_command(name="play", description="Play a song from a URL or search query")
    async def play(self, ctx: discord.ApplicationContext, query: str) -> None:
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.respond("Join a voice channel first.", ephemeral=True)
            return

        await ctx.defer()
        voice_channel = ctx.author.voice.channel
        voice_client = ctx.guild.voice_client or await voice_channel.connect()

        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: self._ytdl.extract_info(query, download=False))
        if "entries" in data:
            data = data["entries"][0]

        source = discord.FFmpegPCMAudio(data["url"], **FFMPEG_OPTIONS)
        if voice_client.is_playing():
            voice_client.stop()
        voice_client.play(source)

        await ctx.respond(f"🎵 Now playing: **{data.get('title', query)}**")

    @discord.slash_command(name="stop", description="Stop playback and leave the voice channel")
    async def stop(self, ctx: discord.ApplicationContext) -> None:
        voice_client = ctx.guild.voice_client
        if voice_client is None:
            await ctx.respond("Not connected to a voice channel.", ephemeral=True)
            return
        await voice_client.disconnect()
        await ctx.respond("👋 Disconnected.")

    @discord.slash_command(name="skip", description="Skip the current song")
    async def skip(self, ctx: discord.ApplicationContext) -> None:
        voice_client = ctx.guild.voice_client
        if voice_client is None or not voice_client.is_playing():
            await ctx.respond("Nothing is playing.", ephemeral=True)
            return
        voice_client.stop()
        await ctx.respond("⏭️ Skipped.")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Music(bot))
