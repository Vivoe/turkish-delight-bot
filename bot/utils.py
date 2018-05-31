import argparse
import asyncio
import io
import json
import logging
import requests


logger = logging.getLogger()

paths = {
    'relic_info': 'data/relic_info.json',
    'part_info': 'data/part_info.json',
    'wanted_list': 'data/wanted_list.json'
}


def to_itemid(item):
    return item.lower().replace(' ', '_')


def pad(s, n):
    return s + ' ' * (n - len(s))


def idx_to_rarity(idx):
    if idx <= 2:
        return 'common'
    elif idx <= 4:
        return 'uncommon'
    else:
        return 'rare'


def get_json(path_id):
    # Use this function. Can go optimize this later into in-memory.
    # Expects elements defined in path variable.
    assert path_id in paths, "Bad path id."

    with open(paths[path_id]) as f:
        d = json.load(f)
    return d


def save_json(path_id, d):
    assert path_id in paths, "Bad path id."

    with open(paths[path_id], 'w') as f:
        json.dump(d, f, indent=4)


def warframe_market_url(item_id):
    return 'https://api.warframe.market/v1/items/' +\
     item_id + '/orders?include=item'


async def async_request(url):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, url)
    return response

#
# Argument parser tricks
#


def catch_async_sys_exit(func):
    async def new_func(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SystemExit as e:
            pass

    return new_func


class DiscordParser(argparse.ArgumentParser):

    # Keep file just to stop complaints.
    # Override everything to print to discord.
    def __init__(self, *args, **kwargs):
        self.arg_stream = io.StringIO()

        super().__init__(*args, **kwargs)

    def print_usage(self, file=None):
        self._print_message(self.format_usage())

    def print_help(self, file=None):
        self._print_message(self.format_help())

    def _print_message(self, message, file=None):
        if message:
            file = self.arg_stream
        file.write(message)

    async def parse_args(self, client, channel, args=None, namespace=None):
        try:
            args, argv = self.parse_known_args(args, namespace)
            if argv:
                msg = ('unrecognized arguments: %s')
                self.error(msg % ' '.join(argv))
            return args
        except SystemExit as e:
            # Get buffer and reset stream.
            logger.info("Throwing sys_exit from argparse help.")
            out = self.arg_stream.getvalue()
            self.arg_stream = io.StringIO()

            # Send message.
            await client.send_message(channel, out)

            raise e
