import argparse
import shlex


async def plat_conversion(client, message):
    raw_args = shlex.split(message.content)[1:]

    parser = argparse.ArgumentParser("!plat")
    parser.add_argument(
        'plat', type=int, help="Number of plats to convert to CAD.")

    args = parser.parse_args(raw_args)

    cad = args.plat * (5.49 / 75.0)

    await client.send_message(message.channel, "Aka $%s." % cad)
