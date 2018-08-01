from bs4 import BeautifulSoup
import os
import steam.webauth as wa
import re
import ast


def scrape_steam(app_id, session):
    cookies = {'birtmetacritic_scorehtime': '283993201', 'mature_content': '1'}
    request_get = session.get('https://store.steampowered.com/app/{}'.format(app_id), cookies=cookies)
    bs = BeautifulSoup(request_get.text.encode('utf-8'), 'lxml')
    tag_bs = bs(text=re.compile('InitAppTagModal'))

    if tag_bs:
        tags = tag_bs[0][tag_bs[0].find('['):tag_bs[0].find(']') + 1]
        tags = re.sub(r',"browseable": true', '', tags)
    else:
        tags = None
    metacritic_score = bs.find('div', {'class': "score high"})

    if metacritic_score:
        metacritic_score = metacritic_score.contents[0].strip()
    else:
        metacritic_score = None

    return tags, metacritic_score


if __name__ == '__main__':
    user = wa.WebAuth(os.environ['STEAM_ID'], os.environ["STEAM_PASSWORD"])
    session = user.login()
    first = True
    with open('data/key_to_apps_dict.txt') as f:
        app_dict = ast.literal_eval(f.read())
    with open('data/tags.txt', 'w') as tags_file:
        with open('data/metacritic_scores.txt', 'w') as metacritic_file:
            tags_file.write('[')
            metacritic_file.write('[')
            for app_id, app_name in app_dict.items():
                tags, metacritic_score = scrape_steam(app_id, session)
                if tags and first:
                    tags_file.write('{"app": ' + str(app_id) + ', "tags": ' + str(tags) + '}')
                    first = False
                if metacritic_score and first:
                    metacritic_file.write('{"app": ' + str(app_id) + ', "metacritic_score": ' + str(metacritic_score) + '}')
                    first = False
                if tags and (not first):
                    tags_file.write(', {"app": ' + str(app_id) + ', "tags": ' + str(tags) + '}')
                if metacritic_score and (not first):
                    metacritic_file.write(', {"app": ' + str(app_id) + ', "metacritic_score": ' + str(metacritic_score) + '}')
                if (not tags) and (not metacritic_score) and (not first):
                    print('No record for: ' + app_name)
            tags_file.write(']')
            metacritic_file.write(']')
