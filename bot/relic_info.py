import logging
from bs4 import BeautifulSoup

import bot.utils as utils


logger = logging.getLogger()


def extract_relic_info_from_droptable(soup):
    """
    DEPRECIATED.
    Updates the drop table from the source page
        http://warframe.wikia.com/wiki/Void_Relic/DropLocationsByRelic

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
    DEPRECIATED
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


async def update_relic_info():
    """
    DEPRECIATED.
    Creates/updates the relic_info.json and part_info.json files.
    Is ok not be async. Makes sense to block message responses until finished.
    """

    logger.info("Update relic info.")

    relic_url = \
        'http://warframe.wikia.com/wiki/Void_Relic/DropLocationsByRelic'
    req = await utils.async_request(relic_url)

    if req.ok:
        soup = BeautifulSoup(req.text, 'html.parser')
    else:
        logger.error("Request to %s has response code %s."
                     % (relic_url, req.status_code))

    relic_info = extract_relic_info_from_droptable(soup)
    part_info = part_to_relic_mapping(relic_info)

    utils.save_json('relic_info', relic_info)
    utils.save_json('part_info', part_info)


def  extract_relic_info(soup):
    """
    Extracts relic information from dedicated relic page.
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

    drop_table = soup.find('table', {'class': 'emodtable'})
    drop_table_rows = drop_table.findChildren('tr', recursive=False)

    drop_items = drop_table_rows[1:7]
    item_names = list(map(lambda r: r.find('td').text.strip(), drop_items))

    drop_loc_table = drop_table_rows[-1].find('table')
    drop_loc_rows = drop_loc_table.findAll('tr', recursive=False)[1:]

    def extract_drop_info(r):
        info = list(map(lambda cell: cell.text.strip(), r.findAll('td')))
        return {
            "tier": info[1],
            "mission_type": info[0], 
            "chance": info[3], 
            "rotation": info[2]
        }

    drop_locations = list(map(extract_drop_info, drop_loc_rows))

    return {
        'drops': item_names,
        'drop_locations': drop_locations
    }


async def get_relic_info(relic_name):
    """
    Gets relic information and caches it, if not already cached.
    Also helps mantain a parts list.
    """

    logger.info("Fetching relic info for %s." % relic_name)

    relic_infos = utils.get_json('relic_info')

    if relic_name in relic_infos:
        return relic_infos[relic_name]

    logger.info("Relic not in database. Searching Wikia.")

    relic_url = "https://warframe.fandom.com/wiki/%s" \
        % relic_name.replace(' ', '_')

    req = await utils.async_request(relic_url)
    if req.ok:
        soup = BeautifulSoup(req.text, 'html.parser')
    else:
        logger.error("Request to %s has response code %s."
                     % (relic_url, req.status_code))

        raise ValueError("Bad relic url.")


    relic_info = extract_relic_info(soup)

    # Cache.
    relic_infos[relic_name] = relic_info
    utils.save_json('relic_info', relic_infos)


    # Update parts mapping.
    part_info = utils.get_json('part_info')

    drops = relic_info['drops']

    for i in range(len(drops)):
        part = utils.to_itemid(drops[i])
        drop_rarity = '%s %s' % (relic, utils.idx_to_rarity(i))

        if part in part_info:
            part_info[part].append(drop_rarity)
        else:
            part_info[part] = [drop_rarity]

   utils.save_json('part_info', part_info)

   return relic_info