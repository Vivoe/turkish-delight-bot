import asyncio
import logging
import time

from bs4 import BeautifulSoup

import bot.utils as utils
from bot.config import config

logger = logging.getLogger()


async def check_alerts(client, channel):
    logger.info("Checking for alerts.")
    wanted_list = utils.get_json('wanted_list')

    url = 'http://deathsnacks.com/wf/'
    req = await utils.async_request(url)

    if req.ok:
        ts = int(time.time())
        soup = BeautifulSoup(req.text, 'html.parser')

        parts = soup.find(
                'ul',
                {'class': ['list-group', 'alerts-container']})\
            .find_all('span', {'class': 'badge'})

        for soup_item in parts:
            item = soup_item.text
            if item.endswith(' Blueprint'):
                item = item[:-10]
            item_id = utils.to_itemid(item)

            users = []
            usernames = []
            for i in range(len(wanted_list)):
                want = wanted_list[i]
                if want['item_id'] == item_id:

                    if (('last_updated' not in want) or
                            # If within the same hour, probably the same alert.
                            (ts - want['last_updated'] >= 60 * 60)):

                        users.append(want['userID'])
                        usernames.append(want['user'])
                        wanted_list[i]['last_updated'] = ts

            if len(users) > 0:
                logger.info('Alert for %s, notifying %s'
                            % (item_id, ', '.join(usernames)))

                for userID in users:
                    user = await client.get_user_info(userID)
                    await client.send_message(
                        user,
                        'Alert for ' +
                        item_id + '\nhttp://deathsnacks.com/wf/')

        utils.save_json('wanted_list', wanted_list)
    else:
        logger.error("Request for %s returned error code %s."
                     % (url, req.status_code))


async def poll(client):
    # Needs a refactor for multi-server.
    default_channel = client.get_server(config['servers'][0])\
        .get_channel(config['default_channel'])

    while True:
        logger.info('Polling.')
        await check_alerts(client, default_channel)
        await asyncio.sleep(60)
