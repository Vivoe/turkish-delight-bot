import shlex

import bot.utils as utils


@utils.catch_async_sys_exit
async def plat_conversion(client, message):
    raw_args = shlex.split(message.content)[1:]

    parser = utils.DiscordParser("!plat")
    parser.add_argument(
        'plat', type=int, help="Number of plats to convert to CAD.")

    args = await parser.parse_args(client, message.channel, raw_args)

    cad = args.plat * (5.49 / 75.0)

    await client.send_message(message.channel, "Aka $%s." % cad)
