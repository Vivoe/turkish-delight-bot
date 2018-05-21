import shlex
import bot.utils as utils
from abc import abstractmethod


class Command:
    @abstractmethod
    def get_parser(self):
        pass

    @abstractmethod
    async def cmd(self, message, args):
        pass

    @utils.catch_async_sys_exit
    async def exec(self, message):
        raw_args = shlex.split(message.content)[1:]
        args = await self.parser.parse_args(
            self.client, message.channel, raw_args)

        await cmd(message, args)

    def __init__(self, client):
        self.client = client
        self.parser = self.get_parser()
        self.cmd = self.parser.prog


class PlatConversionCommand(Command):
    def get_parser(self):
        parser = utils.DiscordParser('!plat')
        parser.add_argument(
            'plat', type=int, help='Number of plats to convert to CAD.')

        return parser

    async def cmd(self, message, args):
        cad = args.plat * (5.49 / 75.0)
        await self.client.send_message(message.channel, "Aka $%s." % cad)
