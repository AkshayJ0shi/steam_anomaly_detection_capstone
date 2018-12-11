import psycopg2 as pg2
from psycopg2.extras import execute_values
from urllib.parse import quote_plus as url
import steam.webauth as wa
import os
import ast
import sys
import pickle
import time
from src.market_to_mongo import *
from datetime import datetime, timedelta


class AnomalyPipeline:
    def __init__(self, last_date=datetime.utcnow().date()-timedelta(32)):
        self.last_date = last_date
        self.anomalies = None

    def update_database(self):
        conn = pg2.connect(dbname='steam_capstone', host='localhost')
        cur = conn.cursor()
        update_list = get_updatable_items(self.last_date, cur)
        session = login_to_steam()
        for i, item in enumerate(update_list):
            if i % 10000 == 9999:  # I want to re-login every once in a while, but I'm afraid to do it too often
                session = login_to_steam()
            update_entry(item, self.last_date, session)
        pass

    def update_dataframe(self):
        pass

    def fit_anomalies(self):
        pass


def login_to_steam():
    user = wa.WebAuth(os.environ['STEAM_ID'], os.environ["STEAM_PASSWORD"])
    return user.login()

def get_updatable_items(date, cursor):
    """
    Looks through the Postgres database to see which items are missing up to date records.
    :param date: datetime.date() object of the latest date to request records for
    :param cursor: psql cursor
    :return: list of item names to request updates for
    """
    item_names = cursor.execute('select distinct(item_name) from sales where date > %(date)s;',
                                {'date': date}).fetchall()
    return [x[0] for x in item_names]

def update_entry(item_name, last_date, session):
    """
    Gets the latest entry of the item, requests data from Steam, then adds all of the missing price points between the
    latest entry and the last_date parameter.
    :param item_name: name of the item
    :param last_date: most recent entry to update database with
    :param session: Steam login session
    :return: None
    """
    conn = pg2.connect(dbname='steam_capstone', host='localhost')
    conn.autocommit = True
    cursor = conn.cursor()

    # Get sales for the item in my database
    cursor.execute(
        """select item_id, date from sales
        where item_name = %(item_name)s
        order by date desc
        limit 1;""", {'item_name':item_name})
    item_id, latest_entry = cursor.fetchone()
    if latest_entry >= last_date:
        pass
    request = get_market_page(session, 730, item_name)

    i = 1
    while request.status_code != 200:
        if i == 9:
            print('Could not update'+item_name)
            pass
        # Try waiting 1 minute, login again, then try waiting 5
        # If it still doesn't work after waiting 5 minutes I'll need to look into the special case
        time.sleep(60*i)
        i += 4
        login_to_steam()
        request = get_market_page(session, 730, item_name)

    price_history = request.json()['prices']
    updates = [(item_id, item_name, datetime.strptime(date[:11], '%b %d %Y').date(), float(price), int(quantity))
               for date, price, quantity in price_history
               if last_date >= datetime.strptime(date[:11], '%b %d %Y').date() > latest_entry]
    if len(updates) == 0:
        pass

    # This acts as a way of recognizing the update in the case of having no sales on that date
    # Could fill in every missing date with 0's
    if updates[-1][2] != last_date:
        updates.append((item_id, item_name, last_date, 0., 0))

    # I read that executemany is slow, possibly because it commits after each execution.
    # Even though it's unlikely my data is on a scale for this to make a difference, I found execute_values as a faster
    # alternative
    query = """insert into sales (item_id, item_name, date, price, quantity)
               values %s;"""
    execute_values(cursor, query, updates)
    conn.close()
    pass


def fill_missing():
    pass
