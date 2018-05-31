import discord
import argparse

import bot.init_bot as init_bot
import bot.auth as authentication
import bot.command_menu as cm

parser = argparse.ArgumentParser()
parser.add_argument(
    '-r', type=str, default=None,
    help="Channel ID from which the bot was restarted from.")

args = parser.parse_args()
auth = None
client = discord.Client()


@client.event
async def on_ready():
    global auth

    auth = authentication.Auth(client)
    await init_bot.init(client, args)


@client.event
async def on_message(message):
    await cm.exec_command(client, auth, message)

client.run(authentication.token())
