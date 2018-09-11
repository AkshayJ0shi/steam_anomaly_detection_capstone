import requests
import sys
from time import sleep

def scrape_page(page):
    return requests.get('http://blog.counter-strike.net/index.php/category/updates/page/{}/'.format(page))

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)
    sys.stdout.write("\033[K")
    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

if __name__ == '__main__':
    for page_num in range(1,48):  # There are 47 pages
        progress(page_num, 47, "Page: " + str(page_num))
        request_return = scrape_page(page_num)
        with open('data/patches/page' + str(page_num) + '.html', 'w') as file:
            file.write(request_return.text)
        sleep(5)