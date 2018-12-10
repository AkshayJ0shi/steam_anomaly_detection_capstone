import psycopg2 as pg2
from urllib.parse import quote_plus as url
import steam.webauth as wa
import os
import ast
import sys
from src.market_to_mongo import *
from datetime import datetime, timedelta


class AnomalyPipeline:
    def __init__(self, last_date=datetime.utcnow().date()-timedelta(32)):
        self.last_date = last_date
        self.anomalies = None

    def update_database(self):
        pass

    def update_dataframe(self):
        pass

    def fit_anomalies(self):
        pass

def get_updatable_items(date):
    """
    Looks through the Postgres database to see which items are missing up to date records.
    :param date: datetime.date() object of the latest date to request records for
    :return: list of item names to request updates for
    """
    conn = pg2.connect(dbname='steam_capstone', host='localhost')
    cur = conn.cursor()
    item_names = cur.execute('select distinct(item_name) from sales where date > %(date)s;', {'date': date}).fetchall()
    return [x[0] for x in item_names]

