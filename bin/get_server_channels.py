import discord
import json
import sys

client = discord.Client()


@client.event
async def on_ready():
    server = client.get_server(sys.argv[1])
    for channel in server.channels:
        print("%s: %s" % (channel.name, channel.id))

    await client.logout()

with open('keys/bot_token.json') as f:
    token = json.load(f)['token']


client.run(token)
