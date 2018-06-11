import json
import logging

from bot.config import config


logger = logging.getLogger()


def token():
    with open('keys/bot_token.json') as f:
        return json.load(f)['token']


class Auth:
    def __init__(self, client):
        logger.info("Init auth.")

        self.servers = config['servers']

        if config['admin_channels'] == '*':
            self.admin_channels = None
        else:
            self.admin_channels = config['admin_channels']

        logger.info("Admin channels: %s" % self.admin_channels)
        logger.info("Servers: %s" % self.servers)

    def authenticate(self, channel):
        logger.debug("Message from channel %s" % channel.id)
        if self.admin_channels is None or channel.id in self.admin_channels:
            return 2
        elif channel.server.id in self.servers:
            return 1
        else:
            return 0
