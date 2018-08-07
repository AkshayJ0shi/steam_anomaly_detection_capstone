from bs4 import BeautifulSoup
import os
import re
from pymongo import MongoClient


def scrape_local_tags(page):
    """
    Extracts the tags and number of people who tagged the game with that category.
    :param page: (str) html app page
    :return: [{"tagid" : 7368, "name" : "Local Multiplayer", "count" : 11}, ...]
    """
    bs = BeautifulSoup(page, 'lxml')
    tag_bs = bs(text=re.compile('InitAppTagModal'))
    if tag_bs:
        tags = tag_bs[0][tag_bs[0].find('['):tag_bs[0].find(']') + 1]
        tags = re.sub(r',"browseable": true', '', tags)
        tags = re.sub(r',"browseable":true', '', tags)
    else:
        tags = None
    return tags


if __name__ == '__main__':
    client = MongoClient()
    db = client['steam_capstone']
    app_page_list = os.listdir('data/games_with_items/')
    for app in app_page_list:
        if app[-5:] != '.html':
            continue
        with open('data/games_with_items/{}'.format(app)) as f:
            page = f.read()
        tags = scrape_local_tags(page)
        if tags:
            tags = eval(tags)
            tags_dict = {'app': app[:-5], 'tags': tags}
            collection_tags = db['tags']
            collection_tags.insert(tags_dict)