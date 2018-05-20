import discord
import sys

import bot.auth as authentication

client = discord.Client()


@client.event
async def on_ready():
    server = client.get_server(sys.argv[1])
    for channel in server.channels:
        print("%s: %s" % (channel.name, channel.id))

    await client.logout()


client.run(authentication.token())
