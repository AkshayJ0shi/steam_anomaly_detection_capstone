from pymongo import MongoClient
from urllib.parse import quote_plus as url
import pandas as pd
import steam.webauth as wa
import os
import ast
import sys


def get_market_page(session, app, item):
    response = session.get('https://steamcommunity.com/market/pricehistory/?appid={}&market_hash_name={}'.format(app, url(item)))
    if response.status_code == 500:
        return 'skip'
    elif response.status_code != 200:
        return None
    else:
        return response


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write("\033[K")
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def calc_num_items(dict):
    total = 0
    for app, items in dict.items():
        for item in items:
            total += 1
    return total

if __name__ == '__main__':
    with open('data/market_item_list.txt') as f:
        item_dict = ast.literal_eval(f.read())
    client = MongoClient()
    db = client['steam_capstone']
    collection = db['skipped']
    collection = db['market']
    user = wa.WebAuth(os.environ['STEAM_ID'], os.environ["STEAM_PASSWORD"])
    session = user.login()
    i = 0
    if i%10000 == 0:
        user = wa.WebAuth(os.environ['STEAM_ID'], os.environ["STEAM_PASSWORD"])
        session = user.login()
    total = calc_num_items(item_dict)
    duplicate = True
    response = True
    for app, items in item_dict.items():
        for item in items.keys():
            progress(i, total, str(app) + ' ' + item)
            i += 1
            if item == 'Kill Covered Sniper Rifle (Minimal Wear)' and app == 440:
                duplicate = False
            if duplicate:
                continue
            response = get_market_page(session, app, item)
            if not response:
                print('Last app: ' + str(app) + ', Last item: ' + item)
                break
            if response == 'skip':
                db['skipped'].insert({'app': app, 'item': item})
                continue
            elif response.json()['success'] == 'false':
                continue
            mongo_dict = {'item_name':item, 'app': app, 'prices':[]}
            for x in response.json()['prices']:
                mongo_dict['prices'].append({'date':x[0], 'median_sell_price':x[1], 'quantity':x[2]})
            collection.insert(mongo_dict)
        if not response:
            break

#244850 Leopard Suit