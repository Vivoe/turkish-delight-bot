import asyncio
import time

from bs4 import BeautifulSoup

import bot.utils as utils
from bot.config import config


async def check_alerts(client, channel):
    wanted_list = utils.get_json('wanted_list')

    url = 'http://deathsnacks.com/wf/'
    req = await utils.async_request(url)

    if req.ok:
        ts = int(time.time())
        soup = BeautifulSoup(req.text, 'html.parser')

        parts = \
            soup.find(
                'ul',
                {'class': ['list-group', 'alerts-container']})\
            .find_all('span', {'class': 'badge'})

        for soup_item in parts:
            item = soup_item.text
            if item.endswith(' Blueprint'):
                item = item[:-10]
            item_id = utils.to_itemid(item)

            users = []
            for i in range(len(wanted_list)):
                want = wanted_list[i]
                if want['item_id'] == item_id:

                    if (('last_updated' not in want) or
                            (ts - want['last_updated'] >= 12 * 60 * 60)):

                        users.append(want['userID'])
                        wanted_list[i]['last_updated'] = ts

            if len(users) > 0:
                await client.send_message(
                    channel,
                    '<@' + users.join('> <@') + '>: Alert for part ' +
                    item_id + '\nhttp://deathsnacks.com/wf/')

        utils.save_json('wanted_list', wanted_list)


async def poll(client):
    # Needs a refactor for multi-server.
    default_channel = client.get_server(config['servers'][0])\
        .get_channel(config['default_channel'])

    while True:
        print("Poll")
        await check_alerts(client, default_channel)
        await asyncio.sleep(60)
