import os
import discord
import asyncio
import asyncudp
from dotenv import load_dotenv
from discord.ext import commands, tasks
from youtubecog import YoutubeCog
load_dotenv(r"C:\Users\daro\PycharmProjects\bot\token.env")
token = os.getenv('TOKEN')
channelid = int(os.getenv('CHANNEL'))
ip = (os.getenv('IP'), int(os.getenv('PORT')))
encoding = os.getenv('ENCODING')
password = os.getenv('PASSWORD')
HEADER = (b'\xFF' * 4)
PINGPACKET = HEADER + bytes("ping", encoding)
PINGRESPONSE = HEADER + bytes("ack", encoding)

class CustomClient(discord.ext.commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        return

    async def on_ready(self):
        self.socket = await asyncudp.create_socket(remote_addr=ip)
        selfaddress = self.socket.getsockname()
        self.socket.sendto(HEADER + bytes('rcon {} log_dest_udp {}:{}'.format(password, selfaddress[0], selfaddress[1]), encoding))
        self.listener.start()
        self.pinger.start()
        return

    async def createnewsocket(self):
        self.socket = await asyncudp.create_socket(remote_addr=ip)
        return

    async def on_message(self, message):
        if message.author == bot.user:
            return
        else:
            if message.channel.id == channelid:
                await self.sender(message)
        await self.process_commands(message)
        return

    @tasks.loop()
    async def listener(self):
        while True:
            try:
                data = await self.socket.recvfrom()
                if data:
                    channel = self.get_channel(channelid)
                    data = data[0][4:]
                    data = data.decode('utf-8')
                    await channel.send(data)
            except:
                pass
            await asyncio.sleep(1)

    async def sender(self, message):
        try:
            msg = str("{}:{}:{}".format(
                message.created_at.time().hour,
                message.created_at.time().minute,
                message.created_at.time().second)) + \
                  ' ' + str(message.author) + ': ' + str(message.content)
            self.socket.sendto(HEADER + bytes('rcon {} say {}'.format(password, msg), encoding))
            pass
        except:
            pass
    @tasks.loop(seconds=30)
    async def pinger(self):
        self.socket.sendto(PINGPACKET)
        return

    async def formatter(self):
        pass


async def setup(bot):
    await bot.add_cog(YoutubeCog(bot))

bot = CustomClient(intents=discord.Intents.all(), command_prefix='$')
asyncio.run(setup(bot))
bot.run(token)
