from bs4 import BeautifulSoup
import os
from pymongo import MongoClient


def scrape_local_mc(page):
    """
    Find the Metacritic score for the .html page
    :param page: (str) html app page
    :return: Metacritic score
    """
    bs = BeautifulSoup(page, 'lxml')
    metacritic_score = bs.find('div', {'class': "score high"})
    if metacritic_score:
        metacritic_score = metacritic_score.contents[0].strip()
    else:
        metacritic_score = None

    return metacritic_score


if __name__ == '__main__':
    client = MongoClient()
    db = client['steam_capstone']
    app_page_list = os.listdir('data/games_with_items/') # list all of the Steam store app pages I've downloaded
    for app in app_page_list:
        if app[-5:] != '.html': # Skips the log file and random .DStore things
            continue
        with open('data/games_with_items/{}'.format(app)) as f:
            page = f.read()
        mc_score = scrape_local_mc(page)
        if mc_score:
            mc_score = eval(mc_score)
            mc_dict = {'app': app[:-5], 'metacritic_score': mc_score}
            collection_tags = db['metacritic']
            collection_tags.insert(mc_dict)