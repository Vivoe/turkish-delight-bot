import json
import discord

from bot.config import config


def token():
    with open('keys/bot_token.json') as f:
        return json.load(f)['token']


class Auth:
    def __init__(self, client):

        self.servers = config['servers']

        if config['admin_channels'] == '*':
            self.admin_channels = None
        else:
            self.admin_channels = config['admin_channels']

    def authenticate(self, channel):
        if self.admin_channels is None or channel.id in self.admin_channels:
            return 2
        elif channel.server in self.servers:
            return 1
        else:
            return 0
