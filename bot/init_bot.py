import os
import json

import bot.utils as utils
import bot.relic_info as ri


def init(client, args):
    print("Bot started.")
    print("Logged in as %s" % client.user.name)

    if not os.path.exists('data'):
        os.mkdir('data')

    if not os.path.exists(utils.paths['wanted_list']):
        with open(utils.paths['wanted_list'], 'w') as f:
            json.dump({}, f)

    ri.update_relic_info()

    if (args.r):
        print("Restarted from %s" % args.r)
        client.send_message(args.r, "Bot restarted!")

    print("Bot ready.")