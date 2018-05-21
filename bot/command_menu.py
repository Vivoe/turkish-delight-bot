import bot.commands as cmds
import bot.auth as auth

async def admin_command_menu(client, message):
    print("Admin command")
    print("Message: %s" % message.content)

    tokens = message.content.split(' ')

    if (tokens[0] == '!!help'):
        await client.send_message(
            message.channel,
            """
            Admin command list:
            !!help
            """)
    else:
        await client.send_message(
            message.channel,
            'Unknown command "%s".' % tokens[0])


async def command_menu(client, message):
    print("Command")
    print("Message: %s" % message.content)

    tokens = message.content.split(' ')

    if tokens[0] == '!help':
        await client.send_message(
            message.channel,
            """
            Command list:
            !help
            !plat n_plat
            """)
    elif tokens[0] == '!plat':
        await cmds.plat_conversion(client, message)
    else:
        await client.send_message(
            message.channel,
            'Unknown command "%s".' % tokens[0])


class CommandMenu:
    def __init__(self, client):
        self.client = client
        self.auth = auth.Auth(client)

        commands = [
            cmds.PlatConversionCommand(client)
        ]

        self.commands = dict(map(lambda c: (c.cmd, c), commands))

        self.help_str = 'Commands:\n' + '\n'.join(
            list(map(
                lambda c: c.parser.format_usage()[7:],
                self.commands.values())))

    async def exec_normal_command(self, message):
        cmd = message.content.split(' ', 1)[0]

        if cmd == '!help':
            await self.client.send_message(message.channel, self.help_str)
        elif cmd in self.commands:
            await self.commands[cmd].exec(message)

    async def exec_command(self, message):
        if message.author.name == 'plat-bot':
            return

        auth_level = self.auth.authenticate(message.channel)

        if (auth_level >= 2 and message.content[:2] == '!!'):
            await admin_command_menu(self.client, message)
        elif message.content[0] == '!':
            await self.exec_normal_command(message)
