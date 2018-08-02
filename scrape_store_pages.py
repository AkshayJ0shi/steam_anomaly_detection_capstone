from bs4 import BeautifulSoup
import os
import steam.webauth as wa
import re
import ast
import requests
import sys

def scrape_page(app_id, session):
    cookies = {'birthtime': '283993201', 'mature_content': '1'}
    return session.get('https://store.steampowered.com/app/{}'.format(app_id), cookies=cookies)


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write("\033[K")
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

# if __name__ == '__main__':
#     user = wa.WebAuth(os.environ['STEAM_ID'], os.environ["STEAM_PASSWORD"])
#     session = user.login()
#     with open('data/key_to_apps_dict.txt') as f:
#         app_dict = ast.literal_eval(f.read())
#     with open('data/ERRORLOG.txt', 'w') as g:
#         total = len(app_dict)
#         for i, (app_id, app_name) in enumerate(app_dict.items()):
#             if i < 290:
#                 continue
#             progress(i, total, app_name)
#             request_return = scrape_page(app_id, session)
#             if request_return.status_code != 200:
#                 g.write(str(app_id) + '/n')
#             elif request_return.url != 'https://store.steampowered.com/':
#                 with open('data/store_pages/' + str(app_id) + '.html', 'w') as file:
#                     file.write(request_return.text)