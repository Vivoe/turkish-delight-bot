import os
import json
import logging
import sys
from datetime import datetime

import bot.utils as utils
from bot.config import config
import bot.relic_info as ri
import bot.poll as poll

logger = logging.getLogger()


async def init(client, args):
    logger.info("Initializing bot.")
    logger.info("Bot started.")
    logger.info("Logged in as %s" % client.user.name)

    if (args.r):
        logger.info("Restarted from %s" % args.r)

        default_channel = client.get_server(config['servers'][0])\
            .get_channel(args.r)
        await client.send_message(default_channel, "Bot restarted!")

    if not os.path.exists('data'):
        logger.info("data directory does not exist. Creating.")
        os.mkdir('data')

    def create_if_not_exists(path, data={}):
        if not os.path.exists(path):
            logger.info("File %s does not exist. Creating." % path)
            with open(path, 'w') as f:
                json.dump(data, f)

    create_if_not_exists(utils.paths['wanted_list'], [])
    create_if_not_exists(utils.paths['relic_info'])
    create_if_not_exists(utils.paths['part_info'])

    await ri.update_relic_info()

    logger.info("Bot ready.")
    await poll.poll(client)
