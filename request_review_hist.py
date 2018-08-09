import requests
import datetime
from pymongo import MongoClient

def get_reviews(app_id):
    """
    Gets {'date': 1517443200, 'recommendations_up': 36508, 'recommendations_down': 6557} for the app id
    :param app: (dict) {app id: app name}
    :return: (list of dicts) [{date: , recommendations_up: , recommendations_down: }, ... ]
    """
    try:
        output = requests.get('https://store.steampowered.com/appreviewhistogram/{}'.format(app_id)) \
         .json()['results']['rollups']
    except:
        return None
    for i, item in enumerate(output):
        item['date'] = str(datetime.datetime.fromtimestamp(item['date']))
        output[i] = item
    output_dict = {'app': str(app_id), 'reviews': output}
    return output_dict


if __name__ == '__main__':
    with open('data/sourced_id_to_name.txt') as f:
        app_dict = eval(f.read())
    client = MongoClient()
    db = client['steam_capstone']
    collection = db['reviews']
    for x in app_dict.keys():
        r = get_reviews(x)
        if r:
            collection.insert(r)