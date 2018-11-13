from bs4 import BeautifulSoup
from datetime import datetime
from os import listdir
from pymongo import MongoClient


if __name__ == '__main__':
    client = MongoClient()
    db = client['steam_capstone']
    collection = db['patches']
    for file_name in listdir('../data/patches/'):
        with open('../data/patches/' + file_name) as f:
            page = f.read()
        bs = BeautifulSoup(page, 'lxml')
        patches = bs.find_all(attrs={'class':'inner_post'})
        date_list = [datetime(*map(int, p.find('p', attrs={'class':'post_date'}).text[:10].split('.'))) for p in patches]
        patch_list = [p.find_all('p', attrs={'class':None}) for p in patches]
        patch_list = [''.join([bs_tags.text for bs_tags in patch]) for patch in patch_list]
        for date, notes in zip(date_list, patch_list):
            collection.insert({'date': date, 'patch_notes':notes})