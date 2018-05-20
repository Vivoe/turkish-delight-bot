paths = {
    'relic_info': 'data/relic_info.json',
    'part_info': 'data/part_info.json',
    'wanted_list': 'data/wanted_list.json'
}


def to_itemid(item):
    return item.lower().replace(' ', '_')


def idx_to_rarity(idx):
    if idx <= 2:
        return 'common'
    elif idx <= 4:
        return 'uncommon'
    else:
        return 'rare'