import discord
from discord.ext import commands
import yt_dlp
import asyncio
test = 0
yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)  # had problems with youtube_dl not getting the correct uploader id


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename


class YoutubeCog(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        pass

    @commands.command(help='Makes the bot play music over a voice channel. This command will invoke joinchannel command if not in voice channel already.')
    async def play(self, ctx, url):
        server = ctx.message.guild
        voice_channel = server.voice_client
        async with ctx.typing():
            filename = await YTDLSource.from_url(url, loop=self.bot.loop)
            voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))  # have to have ffmpeg added to system PATH
        await ctx.send('**Now playing:** {}'.format(filename))
    @play.error
    async def playerror(self, ctx, error):
        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            await ctx.send("Missing required argument " + str(error.args))
        if isinstance(error, discord.ext.commands.BotMissingPermissions):
            await ctx.send("Missing permissions " + str(error.missing_permissions))
        if isinstance(error, discord.ext.commands.BadArgument):
            await ctx.send("Bad argument " + str(error.args))

    @commands.command(help='Stops the music being played.')
    async def stop(self, ctx):
        if ctx.message.guild.voice_client.is_playing():
            await ctx.message.guild.voice_client.stop()
        else:
            await ctx.send("The bot is not playing anything")
        pass

    @commands.command()
    async def pause(self, ctx):
        if ctx.message.guild.voice_client.is_playing():
            await ctx.message.guild.voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything")
        pass

    @commands.command()
    async def resume(self, ctx):
        if ctx.message.guild.voice_client.is_paused():
            await ctx.message.guild.voice_client.resume()
        else:
            await ctx.send("The bot is not playing anything")
        pass

    @commands.command(help='Makes the bot join a voice channel')
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("{} isn't connected to a voice channel".format(str(ctx.message.author.name)))
        else:
            await ctx.message.author.voice.channel.connect()
        return

    @join.error
    async def joinerror(self, ctx, error):
        if isinstance(error, discord.ext.commands.BotMissingPermissions):
            await ctx.send("Missing permissions " + str(error.missing_permissions))
    @commands.command(help='Makes the bot leave a voice channel')
    async def leave(self, ctx):
        if ctx.message.guild.voice_client.is_connected():
            await ctx.message.guild.voice_client.disconnect()
        else:
            await ctx.send("Bot is not connected to any channel")
        pass
