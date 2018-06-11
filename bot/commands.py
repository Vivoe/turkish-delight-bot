import asyncio
from datetime import datetime
import json
import logging
import re
import shlex

from bs4 import BeautifulSoup
from subprocess import Popen

import bot.utils as utils
from bot.config import config
import bot.relic_info as ri


logger = logging.getLogger()


@utils.catch_async_sys_exit
async def plat_conversion(client, message):
    raw_args = shlex.split(message.content)[1:]

    parser = utils.DiscordParser("!plat")
    parser.add_argument(
        'plat', type=int, help="Number of plats to convert to CAD.")

    args = await parser.parse_args(client, message.channel, raw_args)

    cad = args.plat * (5.49 / 75.0)

    await client.send_message(message.channel, "Aka $%.2f." % cad)


@utils.catch_async_sys_exit
async def restart(client, message):
    await client.send_message(message.channel, "Restarting...")

    # Don't know how asyncio will react, as this requires killing the program.
    # Sticking with Popen for now.
    Popen(['./log_run_bot', message.channel.id])


@utils.catch_async_sys_exit
async def get_host_url(client, message):
    if 'host' in config:
        res = await asyncio.create_subprocess_exec(
            './get_aws_addr', config['host'],
            stdout=asyncio.subprocess.PIPE)

        raw_host = await res.stdout.readline()
        host = raw_host.decode('ascii').rstrip()
        print(host)
        if (host == 'null'):
            logger.warning("Hostname misconfigured, check AWS instances.")
            out_message = "Error: Host name misconfigured."
        else:
            out_message = host

        await client.send_message(message.channel, out_message)
    else:
        logger.info("Host not configured")
        await client.send_message(message.channel, "Host not configured.")


@utils.catch_async_sys_exit
async def void_trader(client, message):
    tradeurl = 'http://deathsnacks.com/wf/data/voidtraders.json'

    res = await utils.async_request(tradeurl)
    if res.ok:
        trader_data = json.loads(res.text)[0]

        st_time = datetime \
            .fromtimestamp(trader_data['Activation']['sec']) \
            .strftime('%Y-%m-%d %H:%M:%S')

        out_message = \
            "Void trader info:\n" +\
            trader_data['Character'] + ' @ ' +\
            trader_data['Node'] + ' at ' +\
            st_time

        await client.send_message(message.channel, out_message)
    else:
        logger.error("Request for %s returned error code %s."
                     % (tradeurl, res.status_code))


@utils.catch_async_sys_exit
async def update_relics(client, message):
    await ri.update_relic_info()
    await client.send_message(message.channel, "Relic tables updated.")


@utils.catch_async_sys_exit
async def list_relics(client, message):
    relic_info = utils.get_json('relic_info')
    relics = list(relic_info.keys())

    await client.send_message(
        message.channel,
        "Currently droppable relics:\n" + '\n'.join(relics))


@utils.catch_async_sys_exit
async def add_wanted_part(client, message):
    raw_args = shlex.split(message.content)[1:]

    parser = utils.DiscordParser("!want")
    parser.add_argument('part', type=str, help="The wanted part name.")

    parser.add_argument('--unsafe', action='store_true',
                        help="Do not check for item validity.")

    args = await parser.parse_args(client, message.channel, raw_args)

    item = args.part
    item_id = utils.to_itemid(item)

    user = message.author

    logger.info("item_id: %s, user: %s" % (item_id, user.name))

    market_url = utils.warframe_market_url(item_id)

    if not args.unsafe:
        res = await utils.async_request(market_url)

    if args.unsafe or res.ok:
        parts_info = utils.get_json('part_info')

        drop_relic_list = parts_info.get(item_id)

        new_item = {
            'item_id': item_id,
            'user': user.name,
            'userID': user.id,
            'drop_list': drop_relic_list
        }

        wanted_list = utils.get_json('wanted_list')
        wanted_list.append(new_item)
        utils.save_json('wanted_list', wanted_list)

        logger.info("Adding part.")

        out_message = 'Adding ' + item_id + ' to wanted list for ' +\
                      user.name + '.'

        await client.send_message(message.channel, out_message)
    else:
        logger.warning("Bad item name %s" % item_id)
        await client.send_message(message.channel, "Bad item id.")


@utils.catch_async_sys_exit
async def remove_part(client, message):
    raw_args = shlex.split(message.content)[1:]

    parser = utils.DiscordParser("!remove")
    parser.add_argument('part', type=str, help='The part to remove.')

    args = await parser.parse_args(client, message.channel, raw_args)

    item = args.part
    item_id = utils.to_itemid(item)

    user = message.author

    logger.info("item_id: %s, user: %s" % (item_id, user.name))

    wanted_list = utils.get_json('wanted_list')
    for i in range(len(wanted_list)):
        want = wanted_list[i]
        if want['userID'] == user.id and want['item_id'] == item_id:
            del wanted_list[i]

            utils.save_json('wanted_list', wanted_list)

            out_message = "Removed entry for part " + item_id +\
                " for user " + user.name + "."

            logger.info("Part removed.")
            await client.send_message(
                message.channel,
                out_message)

            return

    # If nothing got deleted, then will end up here.
    logger.info("Could not find matching part for user.")
    out_message = "Could not find entry for part " + item_id +\
        " for user " + user.name + "."

    await client.send_message(
        message.channel,
        out_message)


@utils.catch_async_sys_exit
async def list_wanted(client, message):
    logger.info("list_wanted command.")
    raw_args = shlex.split(message.content)[1:]
    parser = utils.DiscordParser(
        '!listwanted',
        description="List parts wanted by users. Default sorting is by part.")
    parser.add_argument('-t', action='store_true',
                        help="Sort by date posted.")
    parser.add_argument('-u', action='store_true',
                        help="Sort by user.")
    parser.add_argument('-i', action='store_true',
                        help="Sort by item.")

    args = await parser.parse_args(client, message.channel, raw_args)

    wanted_list = utils.get_json('wanted_list')

    if args.t:
        sort_func = lambda x: 0  # Keep order.
    elif args.u:
        sort_func = lambda x: x['user']
    elif args.i:
        sort_func = lambda x: x['item_id']
    else:  # Default: Sort by user.
        sort_func = lambda x: x['user']

    wanted_list.sort(key=sort_func)

    table = [['Part', 'User', 'Drop Loaction']]

    # Convert to table form.
    table_rows = list(map(lambda w: [
        w['user'],
        w['item_id'],
        ', '.join(w['drop_list']) if isinstance(w['drop_list'], list) else ''
    ], wanted_list))

    table.extend(table_rows)

    await utils.print_table(client, message, table, 'Wanted list:')


@utils.catch_async_sys_exit
async def relic_info(client, message):
    raw_args = shlex.split(message.content)[1:]

    parser = utils.DiscordParser("!part")
    parser.add_argument('relic', type=str, help="The requested part.")
    parser.add_argument('-c', action='store_true', help="Sort by chance.")

    args = await parser.parse_args(client, message.channel, raw_args)

    relic_info = utils.get_json('relic_info')

    try:
        groups = re.split(' |_', args.relic)
        era = groups[0].capitalize()
        model = groups[1].capitalize()
        relic_name = era + ' ' + model

        # Used purely to check and throw exception.
        relic_info[relic_name]

    except:
        logging.info("Could not find relic %s" % args.relic)
        await client.send_message(
            message.channel,
            "Relic " + args.relic + " not found.")

        return

    drops = relic_info[relic_name]['drops']

    await client.send_message(
        message.channel,
        'Drops for relic ' + relic_name + ':\n' + '```' +
        'Common:\n' +
        '\t' + drops[0] + '\n' +
        '\t' + drops[1] + '\n' +
        '\t' + drops[2] + '\n' +
        'Uncommon:\n' +
        '\t' + drops[3] + '\n' +
        '\t' + drops[4] + '\n' +
        'Rare:\n' +
        '\t' + drops[5] + '\n' + '```')

    locs = relic_info[relic_name]['drop_locations']

    if args.c:
        logging.info("Sorting by drop chance.")
        locs.sort(key=lambda x: float(x.replace('%', '')))

    header = [['Mission type', 'Category', 'Rotation', 'Chance']]

    table_rows = list(map(lambda x: [
        x['mission_type'],
        x['tier'],
        x['rotation'],
        x['chance']
    ], locs))

    table = header + table_rows

    await utils.print_table(client, message, table, "Drop locations:")


@utils.catch_async_sys_exit
async def parts_info(client, message):
    raw_args = shlex.split(message.content)[1:]

    parser = utils.DiscordParser("!part")
    parser.add_argument("part", type=str, help="The requsted part.")

    args = await parser.parse_args(client, message.channel, raw_args)

    item = args.part
    item_id = utils.to_itemid(item)

    part_info = utils.get_json('part_info')
    if item_id in part_info:
        logging.info("Found relic info for %s." % item_id)
        await client.send_message(
            message.channel,
            'Item ' + item_id + ' is dropped by ' +
            ', '.join(part_info[item_id]) + '.')

    url = utils.warframe_market_url(item_id)
    req = await utils.async_request(url)

    if req.ok:
        data = json.loads(req.text)

        prices = list(map(lambda x: x['platinum'], data['payload']['orders']))
        median = sorted(prices)[len(prices) // 2]

        logging.info("Median price for %s is %s plat." % (item_id, median))

        await client.send_message(
            message.channel,
            "Market price for " + item_id + ": " + str(median) + ' plat.')
    else:
        logging.info("Could not find item in warframe.market.")
        await client.send_message(
            message.channel,
            'Bad item name "' + item + '".')


@utils.catch_async_sys_exit
async def mod_info(client, message):
    raw_args = shlex.split(message.content)[1:]

    parser = utils.DiscordParser("!mod")
    parser.add_argument("mod", type=str, help="The requested mod.")

    args = await parser.parse_args(client, message.channel, raw_args)

    item_id = utils.to_itemid(args.mod)
    wikia_id = utils.to_wikiaid(item_id)

    url = 'http://warframe.wikia.com/wiki/' + wikia_id

    req = await utils.async_request(url)

    if req.ok:
        soup = BeautifulSoup(req.text, 'html.parser')
        image_url = soup.find('img', {'class': 'pi-image-thumbnail'})\
            .attrs['src']

        await client.send_message(message.channel, image_url)
    else:
        await client.send_message(
            message.channel,
            "Could not find mod %s." % item_id)


@utils.catch_async_sys_exit
async def weapon_info(client, message):
    raw_args = shlex.split(message.content)[1:]

    parser = utils.DiscordParser(
        "!drop",
        description="Drop locations for prime items.")
    parser.add_argument(
        "item", type=str,
        help="The requested weapon/warframe.")

    args = await parser.parse_args(client, message.channel, raw_args)

    item_id = utils.to_itemid(args.item)
    if not item_id.endswith('_prime'):
        item_id += '_prime'

    wikia_id = utils.to_wikiaid(item_id)

    url = 'http://warframe.wikia.com/wiki/' + wikia_id

    req = await utils.async_request(url)

    if req.ok:
        # try:
        soup = BeautifulSoup(req.text, 'html.parser')

        # Disambiguation between warframes and weapons.

        # Table rows.
        drop_table = soup.find('b', string='Drop Locations')\
            .next.next.next

        warframe_table = drop_table.find(
            'div',
            {'class': 'tabbertab', 'title': 'PC'})

        if warframe_table:
            table = warframe_table
        else:
            table = drop_table

        if not warframe_table:
            man_table = soup.find('table', {'class': 'foundrytable'})
            mats_row = man_table.find_all('tr', recursive=False)[1]
            mats_soup = mats_row.find_all('td')[:5]

            mats_str = '\nRequired materials:\n'
            for mat_soup in mats_soup:
                if mat_soup.text.strip() == '':
                    break

                mat = mat_soup.find('a').attrs['title']
                mat_count = mat_soup.text.strip()

                mats_str += '\t%s: %s\n' % (mat, mat_count)

        trs = table.find_all('tr')

        message_str = 'Drop locations for %s:\n```\n' % item_id
        for tr in trs:
            td = tr.find_all('td')
            part = td[0].text.strip()

            drop_locations = \
                BeautifulSoup(
                    str(td[1]).replace('<br/>', '\n'),
                    'html.parser') \
                .text.strip().split('\n')

            message_str += part + '\n'

            for drop_loc in drop_locations:
                message_str += '\t' + drop_loc + '\n'

        message_str += mats_str + '```'

        await client.send_message(
            message.channel,
            message_str)
    else:
        await client.send_message(
            message.channel,
            "Could not find prime item %s." % item_id)
