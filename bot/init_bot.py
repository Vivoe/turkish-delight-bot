import os
import json

import bot.utils as utils
from bot.config import config
import bot.relic_info as ri
import bot.poll as poll


async def init(client, args):
    print("Bot started.")
    print("Logged in as %s" % client.user.name)

    if (args.r):
        print("Restarted from %s" % args.r)
        print(config)

        default_channel = client.get_server(config['servers'][0])\
            .get_channel(args.r)
        await client.send_message(default_channel, "Bot restarted!")

    if not os.path.exists('data'):
        os.mkdir('data')

    def create_if_not_exists(path, data={}):
        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump(data, f)

    create_if_not_exists(utils.paths['wanted_list'], [])
    create_if_not_exists(utils.paths['relic_info'])
    create_if_not_exists(utils.paths['part_info'])

    await ri.update_relic_info()

    print("Bot ready.")
    await poll.poll(client)


