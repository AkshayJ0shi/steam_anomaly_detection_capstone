import psycopg2 as pg2
from psycopg2.extras import execute_values
import os
import pandas.io.sql as sqlio
import pickle
import time
from src.market_to_mongo import *
from src.arima_anom_detect import run_detection, print_top, anom_consensus
from datetime import datetime, timedelta
from random import sample

# My first instinct was to make this a class in order to save progress and easily access the models and anomalies.
# This proved unnecessary in the end.
# class AnomalyPipeline:
#     def __init__(self, last_date=datetime.utcnow().date()-timedelta(32)):
#         if last_date > datetime.utcnow().date()-timedelta(32):
#             last_date = datetime.utcnow().date()-timedelta(32)  # Cannot use data more recently than this
#         self.last_date = last_date
#         self.anomalies = None

def update_database(update_date=datetime.utcnow().date()-timedelta(32)):
    terminal_display('Getting item list...')
    update_date = min(update_date, datetime.utcnow().date()-timedelta(32))
    conn = pg2.connect(dbname='steam_capstone', host='localhost')
    cur = conn.cursor()
    update_list = get_updatable_items(update_date, cur)
    session = login_to_steam()
    for i, (item, latest_entry) in enumerate(update_list):
        progress(i, len(update_list), item)
        if i % 10000 == 9999:  # I want to re-login every once in a while, but I'm afraid to do it too often
            session = login_to_steam()
        update_item(item, update_date, latest_entry, session)

def update_item(item_name, last_date, latest_entry, session):
    """
    Gets the latest entry of the item, requests data from Steam, then adds all of the missing price points between the
    latest entry and the last_date parameter.
    :param item_name: name of the item
    :param last_date: most recent entry to update database with
    :param latest_entry: the item's most recent data point
    :param session: Steam login session
    :return: None
    """
    if latest_entry >= last_date:
        return None
    conn = pg2.connect(dbname='steam_capstone', host='localhost')
    conn.autocommit = True
    cursor = conn.cursor()

    # Get sales for the item in my database
    cursor.execute(
        """select item_id from id
        where item_name = %(item_name)s;""", {'item_name':item_name})
    item_id = cursor.fetchone()[0]

    request = get_market_page(session, 730, item_name)
    i = 1
    while request.status_code != 200:
        # Try waiting 1 minute, login again, then try waiting 5
        # If it still doesn't work after waiting 5 minutes I'll need to look into the special case
        if i == 9:
            print('Could not update'+item_name)
            return None
        time.sleep(60*i)
        i += 4
        login_to_steam()
        request = get_market_page(session, 730, item_name)

    price_history = request.json()['prices']
    updates = [(item_id, item_name, datetime.strptime(date[:11], '%b %d %Y').date(), float(price), int(quantity))
               for date, price, quantity in price_history
               if last_date >= datetime.strptime(date[:11], '%b %d %Y').date() > latest_entry]

    # This acts as a way of recognizing the update in the case of having no sales on that date
    # Could fill in every missing date with 0's
    if len(updates) == 0 or updates[-1][2] != last_date:
        updates.append((item_id, item_name, last_date, 0., 0))

    # I read that executemany is slow, possibly because it commits after each execution.
    # Even though it's unlikely my data is on a scale for this to make a difference, I found execute_values as a faster
    # alternative
    query = """insert into sales (item_id, item_name, date, price, quantity)
               values %s;"""
    execute_values(cursor, query, updates)
    conn.close()

def fit_anom_from_db(**kwargs):
    """
    Make a minimal df in memory from the data in the database, then run anomaly detection from that.
    :param kwargs: options listed below
    :param min_price: minimum price threshold for removing data
    :param min_quant: minimum quantity threshold for removing data
    :param days_released: number of days at the start of the time series to remove. Items almost universally sell for
    many times more than they do several days later
    :param arima: <bool> smooth with arima or not
    :return: print top 10 anomalies for now
    """
    terminal_display('Creating DataFrame...')
    conn = pg2.connect(dbname='steam_capstone', host='localhost')
    query = 'select * from sales order by item_name, date;'
    df = sqlio.read_sql_query(query, conn, parse_dates=['date'])
    df.columns = ['item_id', 'item_name', 'timestamp', 'median_sell_price', 'quantity']
    df = df.drop(columns=['item_id'])
    df['days_since_release'] = df.groupby('item_name')['timestamp']\
        .transform(lambda x: map(lambda y: y.days, x-min(x)))
    terminal_display('Beginning anomaly detection...')
    print_top(run_detection('data/anoms_from_db.pkl', **kwargs), n=10)

# Gather and filter the data with a single SQL query for fun
def fit_anom_sql(min_price=.15, min_quant=30, days_released=45):
    """
    A single SQL query to skip the filtering step when creating the dataframe
    :param min_price, min_quant, days_released: filter parameters
    :return: filtered dataframe
    """
    conn = pg2.connect(dbname='steam_capstone', host='localhost')
    query = (
        """
        select t_days_released.item_name, t_days_released.date as timestamp, t_days_released.price as median_sell_price 
        from (select *, count(*) over (partition by item_name order by date asc) as days_released from sales) as t_days_released
        inner join (select item_name 
                    from (select *, count(*) over (partition by item_name order by date asc) as days_released from sales) as t 
                    where days_released > %(days_released)s 
                    group by item_name 
                    having min(price) > %(min_price)s and min(quantity) > %(min_quant)s) as t_keep_items
        on t_days_released.item_name = t_keep_items.item_name
        where days_released > %(days_released)s
        order by t_days_released.item_name, timestamp;
        """)
    df = sqlio.read_sql_query(query, conn, parse_dates=['timestamp'],
                              params={'min_price': min_price, 'min_quant': min_quant+1, 'days_released': days_released})
    print_top(anom_consensus(df), n=10)


# UTILITY
def terminal_display(message):
    """
    Utility function to display progress messages in the terminal.
    :param message: Message to display
    """
    # sys.stdout.write("\033[K")
    sys.stdout.write('\r'+message)
    sys.stdout.flush()

def login_to_steam():
    """
    Must be logged into an account to make requests from Steam
    :return: session object
    """
    user = wa.WebAuth(os.environ['STEAM_ID'], os.environ["STEAM_PASSWORD"])
    return user.login()

def get_updatable_items(date, cursor):
    """
    Looks through the Postgres database to see which items are missing up to date records.
    :param date: datetime.date() object of the latest date to request records for
    :param cursor: psql cursor
    :return: list of item names to request updates for
    """
    cursor.execute('select distinct(item_name), max(date) from sales group by item_name having max(date) < %(date)s;',
                                {'date': date})
    return cursor.fetchall()


if __name__ == '__main__':
    update_database(update_date=datetime(2018, 11, 10).date()) # using manual date to avoid the 2 hour wait while it
                                                               # updates a couple of data points
    fit_anom_from_db(min_price=.15, min_quant=30, days_released=45)
