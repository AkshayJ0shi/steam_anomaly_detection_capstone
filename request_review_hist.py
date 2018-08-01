import requests
import ast
import datetime

def get_reviews(app_id, app_name):
    """
    Gets {'date': 1517443200, 'recommendations_up': 36508, 'recommendations_down': 6557} for the app id
    :param app: (dict) {app id: app name}
    :return: (list of dicts) [{date: , recommendations_up: , recommendations_down: }, ... ]
    """
    try:
        output = requests.get('https://store.steampowered.com/appreviewhistogram/{}'.format(app_id)) \
         .json()['results']['rollups']
    except:
        print('No reviews for ' + app_name)
        return None
    for i, item in enumerate(output):
        item['app'] = app_id
        item['date'] = datetime.datetime.fromtimestamp(item['date'])
        output[i] = item
    return output


# I'll need to go back and check for non 200's. Seems like it's been a long time since I got a "No reviews for " message
# I can find the first non 200, then check the app id of the previous entry to get my starting point
if __name__ == '__main__':
    with open('data/key_to_apps_dict.txt') as f:
        app_dict = ast.literal_eval(f.read())

    # For now write to file, later write to mongo
    with open('data/reviews.txt', 'w') as g:
        for app_id, app_name in app_dict.items():
            reviews = get_reviews(app_id, app_name)
            if reviews:
                g.write(str(reviews))


# Code to fix formatting to be able to evaluate with eval():
# string = re.sub(r'\]\[', '],[', string)
# string = '[' + string
# string = string + ']'
# b = eval(string)
# for x in range(len(b)):
#     for y in range(len(b[x])):
#         b[x][y]['date'] = str(b[x][y]['date'])
