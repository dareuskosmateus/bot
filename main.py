import os
import discord
import asyncio
import asyncudp
import re
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
        self.channel = self.get_channel(1083108054486224896)
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
                    formatted = await self.formatter(data)
                    if formatted:
                        await self.channel.send(formatted)
            except Exception as e:
                print(repr(e))
            await asyncio.sleep(1)

    async def sender(self, message):
        try:
            msg = str("{}:{}:{}".format(
                str('0' + str(message.created_at.time().hour))[-2:],
                str('0' + str(message.created_at.time().minute))[-2:],
                str('0' + str(message.created_at.time().second))[-2:] + \
                  ' ' + str(message.author) + ': ' + str(message.content)))
            self.socket.sendto(HEADER + bytes('rcon {} say {}'.format(password, msg), encoding))
            pass
        except:
            pass

    @tasks.loop(seconds=30)
    async def pinger(self):
       self.socket.sendto(PINGPACKET)
       data = await self.socket.recvfrom()
       await asyncio.sleep(0.5)
       if data:
           return
       else:
           await self.channel.send("Lost connection to the server")
       return

    async def formatter(self, data):
        data = data[0]
        if data.startswith(HEADER):
            data = data[4:]
        if data.startswith(b'n'):
            data = data[1:]
            if data.startswith(b'\x01'):
                data = data[3:]
                data = data.decode('utf-8')
                data = re.split('\^7:', data)
                nickname, message = data[0], data[1]
                nickname = re.sub("(\^x...)", '', nickname)
                nickname = re.sub("(\^[0-9])", '', nickname)
                string = "> " + nickname + ": " + message #discord formatting
                return string
                pass
        pass


async def setup(bot):
    await bot.add_cog(YoutubeCog(bot))

bot = CustomClient(intents=discord.Intents.all(), command_prefix='$')
asyncio.run(setup(bot))
bot.run(token)
