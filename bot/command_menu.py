import logging

import bot.commands as cmds

logger = logging.getLogger()


async def admin_command_menu(client, message):
    logger.info("Admin command: %s" % message.content)

    tokens = message.content.split(' ')

    if (tokens[0] == '!!help'):
        logger.info("Admin help")
        await client.send_message(
            message.channel,
            """
            Admin command list:
            !!help
            !!restart
            !!host
            """)
    elif tokens[0] == "!!restart":
        await cmds.restart(client, message)
    elif tokens[0] == "!!host":
        await cmds.get_host_url(client, message)
    else:
        logger.info("Unknown admin command %s" % message.content)
        await client.send_message(
            message.channel,
            'Unknown command "%s".' % tokens[0])


async def command_menu(client, message):
    # print("Message: %s" % message.content)
    logger.info("Regular command: %s" % message.content)

    tokens = message.content.split(' ')

    if tokens[0] == '!help':
        logger.info("Help")
        await client.send_message(
            message.channel,
            """
            Command list:
            !help
            !plat n_plat
            !voidtrader
            !updaterelics
            !listrelics
            !want part
            !remove part
            !listwanted
            !relic relic
            !part part
            """)
    elif tokens[0] == '!plat':
        await cmds.plat_conversion(client, message)
    elif tokens[0] == '!voidtrader':
        await cmds.void_trader(client, message)
    elif tokens[0] == '!updaterelics':
        await cmds.update_relics(client, message)
    elif tokens[0] == '!listrelics':
        await cmds.list_relics(client, message)
    elif tokens[0] == '!want':
        await cmds.add_wanted_part(client, message)
    elif tokens[0] == '!remove':
        await cmds.remove_part(client, message)
    elif tokens[0] == '!listwanted':
        await cmds.list_wanted(client, message)
    elif tokens[0] == '!relic':
        await cmds.relic_info(client, message)
    elif tokens[0] == '!part':
        await cmds.parts_info(client, message)
    else:
        logger.info("Unknown command %s." % message.content)
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
