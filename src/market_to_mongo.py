import os
import sys
import ast

from urllib.parse import quote_plus as url
from pymongo import MongoClient

import steam.webauth as wa


def get_market_page(session, app, item):
    """
    Requests the market data for the (app)'s (item)
    :param session: wa session. I have to be logged in to request
    :param app: (int) id of app
    :param item: (str) item name to be converted to url
    :return: get response
    """
    response = session.get('https://steamcommunity.com/market/pricehistory/?appid={}&market_hash_name={}'.format(app, url(item)))
    if response.status_code == 500: # Some items I have aren't actually on the market and they return 500
        return 'skip'
    elif response.status_code != 200:
        return None
    else:
        return response


def progress(count, total, status=''):
    """
    Progress bar
    """
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write("\033[K")
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

def calc_num_items(item_dict):
    """
    Calculates the total number of items to be used in the progress bar
    """
    return sum([len(items) for items in item_dict.values()])

if __name__ == '__main__':
    with open('../data/market_item_list.txt') as f:
        item_dict = ast.literal_eval(f.read()) # This file looks like [{app_id: app_name}...]
    client = MongoClient()
    db = client['steam_capstone']
    collection = db['skipped']
    collection = db['market']
    user = wa.WebAuth(os.environ['STEAM_ID'], os.environ["STEAM_PASSWORD"])
    session = user.login() # login to Steam
    i = 0
    if i%10000 == 0: # Re-login every 10000 items
        user = wa.WebAuth(os.environ['STEAM_ID'], os.environ["STEAM_PASSWORD"])
        session = user.login()
    total = calc_num_items(item_dict)
    duplicate = True # If I need to restart, I want to record how many items I've been through for the progress bar
    response = True
    last_item = 'Leopard Suit' # Manually placed when the script is paused
    last_app = 244850 # Manually placed when the script is paused
    for app, items in item_dict.items():
        for item in items.keys():
            progress(i, total, str(app) + ' ' + item)
            i += 1
            if item == last_item and app == last_app: # Keep looping until I'm back at the last item
                duplicate = False
            if duplicate: # Skip items I've already requested
                continue
            response = get_market_page(session, app, item)
            if not response: # If I keyboard interput or it returns something other than 200, break and print last item
                print('Last app: ' + str(app) + ', Last item: ' + item)
                break
            if response == 'skip': # Keep a record of which items apparently aren't on the market, just to be safe
                db['skipped'].insert({'app': app, 'item': item})
                continue
            elif response.json()['success'] == 'false': # If the item has never sold, continue
                continue
            mongo_dict = {'item_name':item, 'app': app, 'prices':[]}
            for x in response.json()['prices']: # Write to Mongo
                mongo_dict['prices'].append({'date':x[0], 'median_sell_price':x[1], 'quantity':x[2]})
            collection.insert(mongo_dict)
        if not response: # If something goes wrong, pause the script
            break
