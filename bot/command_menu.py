import bot.commands as cmds

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


async def exec_command(client, auth, message):
    if message.author.name == 'plat-bot':
        return

    auth_level = auth.authenticate(message.channel)

    if (auth_level >= 2 and message.content[:2] == '!!'):
        await admin_command_menu(client, message)
    elif message.content[0] == '!':
        await command_menu(client, message)