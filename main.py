import socket
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv(r"C:\Users\daro\PycharmProjects\bot\token.env")
token = os.getenv('TOKEN')
channel = int(os.getenv('CHANNEL'))
ip = (os.getenv('IP'), int(os.getenv('PORT')))
encoding = os.getenv('ENCODING')
password = os.getenv('PASSWORD')
HEADER = (b'\xFF' * 4)

class CustomClient(discord.ext.commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soc.connect(ip)
        self.soc.settimeout(1)

    async def createsocket(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.soc.connect(ip)
        self.soc.settimeout(1)
        return

    async def on_ready(self):
        return

    async def on_message(self, message):
        if message.author == bot.user:
            return
        else:
            if message.channel.id == channel:
                await self.send_listen(message)
        return

    async def send_listen(self, message):
        try:
            msg = str("{}:{}:{}".format(message.created_at.time().hour, message.created_at.time().minute, message.created_at.time().second)) +\
                  ' ' + str(message.author) + ': ' + str(message.content)
            self.soc.sendto(HEADER + bytes('rcon {} say {}'.format(password, msg), encoding), ip)
        except ConnectionRefusedError:
            message.channel.send("Connection refused " + str(socket.error))
        except ConnectionAbortedError:
            message.channel.send("Connection aborted " + str(socket.error))
        except ConnectionResetError:
            message.channel.send("Connection reset " + str(socket.error))
        except ConnectionError:
            message.channel.send("XD")
        return


bot = CustomClient(intents=discord.Intents.all(), command_prefix='$')
bot.run(token)
