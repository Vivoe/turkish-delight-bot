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

buildable = [
    'systems',
    'chassis',
    'neuroptics',
    'cerebrum',
    'carapace'
]


def to_itemid(item):
    item_id = item.lower().replace(' ', '_')
    item_tokens = item_id.split('_')
    if item_id.endswith('_blueprint') and item_tokens[-2] in buildable:
        item_id = item_id[:-10]
    return item_id


def to_wikiaid(item_id):
    return '_'.join(list(map(lambda x: x.capitalize(), item_id.split('_'))))


def pad(s, n, tab=True):
    assert n - len(s) >= 0, "Cannot pad length less than string length."

    # Use tabs to save character count.
    if tab:
        padlen = n - len(s)
        n_tabs = padlen // 4
        n_spaces = padlen % 4
        return s + '\t' * n_tabs + ' ' * n_spaces
    else:
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


async def print_table(client, message, table, title=None):
    """
    Table is a list of rows.
    """

    n_cols = len(table[0])
    n_rows = len(table) - 1  # Don't include header.

    def get_col_width(row):
        max_len = max(map(len, row))
        return max(5, max_len) + 5

    # Transpose table, take max.
    col_widths = list(map(get_col_width, zip(*table)))
    table_width = sum(col_widths) + 2 * (n_cols - 1)

    def to_row(row):
        return '| '.join(list(map(
            lambda sl: pad(sl[0], sl[1]),
            zip(row, col_widths)))) + '\n'

    header = to_row(table[0])
    header += ('-' * table_width) + '\n'

    i = 0
    if title:
        table_str = title + '\n```\n' + header
    else:
        table_str = '\n```\n' + header

    while i < n_rows:
        row = table[i + 1]  # Offset for header.

        table_row = to_row(row)

        if len(table_str) + len(table_row) < 1995:
            table_str += table_row
            i += 1
        else:
            table_str += '```'
            await client.send_message(message.channel, table_str)
            if title:
                table_str = title + '\n```\n' + header
            else:
                 table_str = '\n```\n' + header

    table_str += '```'
    await client.send_message(message.channel, table_str)


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
