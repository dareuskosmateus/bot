import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import ffmpeg
class YoutubeCog(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        pass

    @commands.command(help='Makes the bot play music over a voice channel. This command will invoke joinchannel command if not in voice channel already.')
    async def play(self, ctx):
        if not ctx.message.author.voice:
            await self.joinchannel(ctx)

        pass

    @commands.command(help='Stops the music being played.')
    async def stop(self, ctx):
        pass

    @commands.command()
    async def pause(self, ctx):
        pass

    @commands.command()
    async def resume(self,ctx):
        pass


    @commands.command(help='Makes the bot join a voice channel')
    async def join(self, ctx):
        if not ctx.message.author.voice:
            await ctx.send("{} isn't connected to a voice channel".format(str(ctx.message.author.name)))
        else:
            await ctx.message.author.voice.channel.connect()
        return

    @commands.command(help='Makes the bot leave a voice channel')
    async def leave(self, ctx):
        if ctx.message.guild.voice_client.is_connected():
            await ctx.message.guild.voice_client.disconnect()
        else:
            await ctx.send("Bot is not connected to any channel")
        pass
