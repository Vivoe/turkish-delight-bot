import discord
import argparse
import logging
import sys
import traceback
from datetime import datetime

logger = logging.getLogger()

parser = argparse.ArgumentParser()
parser.add_argument(
    '-r', type=str, default=None,
    help="Channel ID from which the bot was restarted from.")
parser.add_argument(
    '--stdout', action='store_true',
    help="Print logging to stdout.")
parser.add_argument(
    '--debug', action='store_true',
    help='Print debug logs.')

args = parser.parse_args()

# Initialize logger before anything else.
logger = logging.getLogger()

log_ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Logging for boterr.log file.
print('Starting bot at %s' % log_ts)

if args.stdout:
    handler = logging.StreamHandler(sys.stdout)
else:
    handler = logging.FileHandler('logs/bot_%s.log' % log_ts)

if args.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s [%(filename)s - %(funcName)s@%(lineno)d]:' +
    ' %(message)s',
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
    try:
        await init_bot.init(client, args)
    except:
        logger.error(traceback.format_exc())


@client.event
async def on_message(message):
    try:
        await cm.exec_command(client, auth, message)
    except:
        logger.error(traceback.format_exc())

client.run(authentication.token())
