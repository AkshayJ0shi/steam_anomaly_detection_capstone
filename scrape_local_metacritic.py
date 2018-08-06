from bs4 import BeautifulSoup
import os
import steam.webauth as wa
import re
import ast
from pymongo import MongoClient


def scrape_local_mc(page):
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
    app_page_list = os.listdir('data/games_with_items/')
    for app in app_page_list:
        if app[-5:] != '.html':
            continue
        with open('data/games_with_items/{}'.format(app)) as f:
            page = f.read()
        mc_score = scrape_local_mc(page)
        if mc_score:
            mc_score = eval(mc_score)
            mc_dict = {'app': app[:-5], 'metacritic_score': mc_score}
            collection_tags = db['metacritic']
            collection_tags.insert(mc_dict)