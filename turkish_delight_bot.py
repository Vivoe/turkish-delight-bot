import discord
import argparse
import logging
import sys
from datetime import datetime

logger = logging.getLogger()

parser = argparse.ArgumentParser()
parser.add_argument(
    '-r', type=str, default=None,
    help="Channel ID from which the bot was restarted from.")
parser.add_argument(
    '--stdout', action='store_true',
    help="Print logging to stdout.")

args = parser.parse_args()

# Initialize logger before anything else.
logger = logging.getLogger()

log_ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

if args.stdout:
    handler = logging.StreamHandler(sys.stdout)
else:
    handler = logging.FileHandler('logs/bot_%s.log' % log_ts)

logger.setLevel(logging.INFO)
# handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

logger.addHandler(handler)


import bot.init_bot as init_bot
import bot.auth as authentication
import bot.command_menu as cm


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
