import json
import os

import requests
from bs4 import BeautifulSoup

import bot.utils as utils


def extract_relic_info(soup):
    """
    Extracts relic information from the Warframe wikia.
    Returns a dictionary of all active relics.
    return: {
        'relic name': {
            'drops': [Parts],
            'drop_locations': [
                {
                    'mission_type': mission,
                    'tier': tier,
                    'rotation': rotation,
                    'chance': chance
                }
            ]
        }
    }
    """

    # Get the tables corresponding to Lith, Meso, Neo, Axi
    # These are the tables in the tabbed layout.
    era_tables = soup.find_all('table', {'class': 'article-table'})

    # Dictionary to store relic info results.
    relic_info = {}

    for era_table in era_tables:

        # Each era table contains info for each relic as a row in a
        #   table-like format.

        # Structure for a relic table/row:
        # Relic name\n List of relic drops & Table for drop locations

        # First row is a header.
        relic_tables = era_table.find_all('tr', recursive=False)[1:]

        for relic_table in relic_tables:
            relic = next(relic_table.stripped_strings)

            # Separate out the two sides of the table.
            drop_soup, drop_locations_table_soup = \
                relic_table.find_all('td', recursive=False)

            # Get relic drops.
            # First element in the text is the name of the relic.
            # After that, the text is the list.
            drops = list(drop_soup.stripped_strings)[1:]

            # Get relic drop location information.
            # Get all rows in drop table, excluding header.
            drop_locations_soup = drop_locations_table_soup.find_all('tr')[1:]

            # Format each row into a dictionary.
            drop_locations = list(map(
                lambda drop_location_soup: {
                    'mission_type': drop_location_soup[0],
                    'tier': drop_location_soup[1],
                    'rotation': drop_location_soup[2],
                    'chance': drop_location_soup[3]
                },
                map(
                    lambda s: list(s.stripped_strings),
                    drop_locations_soup)))

            relic_info[relic] = {
                'drops': drops,
                'drop_locations': drop_locations
            }

    return relic_info


def part_to_relic_mapping(relic_info):
    """
    Converts the relic_info dictionary into a part-first dictionary.
    return: {
        'part': [
            '$relic_name $rarity'
        ]
    }
    """
    parts = {}

    for relic in relic_info:
        drops = relic_info[relic]['drops']

        for i in range(len(drops)):
            part = utils.to_itemid(drops[i])
            drop_rarity = '%s %s' % (relic, utils.idx_to_rarity(i))

            if part in parts:
                parts[part].append(drop_rarity)
            else:
                parts[part] = [drop_rarity]

    return parts


def update_relic_info():
    """
    Creates/updates the relic_info.json and part_info.json files.
    """

    relic_url = \
        'http://warframe.wikia.com/wiki/Void_Relic/DropLocationsByRelic'
    req = requests.get(relic_url)

    soup = BeautifulSoup(req.text, 'html.parser')

    relic_info = extract_relic_info(soup)
    part_info = part_to_relic_mapping(relic_info)

    with open(utils.paths['relic_info'], 'w') as f:
        json.dump(relic_info, f, indent=4)

    with open(utils.paths['part_info'], 'w') as f:
        json.dump(part_info, f, indent=4)
