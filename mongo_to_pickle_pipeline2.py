from pymongo import MongoClient
import pickle
import pandas as pd
import numpy as np
from tqdm import tqdm
import time
import datetime

def get_cursor(app=None):
    """
    Get a mongo cursor to query a single app (or every app if no param is given)
    :param app: (int) id of app
    :return:
    """
    client = MongoClient()
    db = client.steam_capstone
    collection = db.market
    if app:
        return collection.find({'app': app})
    else:
        return collection.find()


def split_col(df, lst_col='prices'):
    """
    Takes a column with a list of dicts as entries and turns each dict entry into its own row,
     and each key into a column.
    :param df:
    :param lst_col: 'prices' looks like: [{'date':date, 'median_sell_price':msp, 'quantity':quantity}, ...]
    :return:
    """
    df = pd.DataFrame({col: np.repeat(df[col].values, df[lst_col].str.len())
                         for col in df.columns.difference([lst_col])}) \
             .assign(**{lst_col: np.concatenate(df[lst_col].values)})[df.columns.tolist()]
    df[['date', 'median_sell_price', 'quantity']] = pd.DataFrame(df.prices.values.tolist(), index=df.index)
    df['quantity'] = list(map(int, df['quantity']))
    return df.drop(columns='prices')


def strip_hours(df):
    """
    Strips off the hour stamp from the date to prepare it for comparison and transformation to datetime object.
    :param df:
    :return:
    """
    df.date = [x[:11] for x in df.date]
    return df


def remove_non_daily(df):
    """
    Removes all entries that are not daily median/price data points. (The last month of entries are hourly)
    :param df:
    :return:
    """
    return df[df.groupby(by=['item_name', 'app', 'date'], as_index=False).transform('count').quantity == 1]


def transform_to_datetime(a):
    """
    Transforms the formatted date to a datetime object
    :param df:
    :return:
    """
    s = pd.Series(name='date')
    for i, x in enumerate(a['prices']):
        s = s.append(pd.Series(pd.to_datetime(x['date'][:11]), index=[i]))


def pickle_df(df, filename):
    """
    Saves the df into a pickle
    :param df: clean df
    :param filename: (str) name of .pkl file
    :return:
    """
    with open(filename + '.pkl', 'wb') as f:
        pickle.dump(df, f)



def mongo_to_clean_df_pipeline(filename, app=None, cursor=False):
    """
    Creates pickle file of a cleaned dataframe
    :param filename: (str) name of pickle file
    :param app: (int) id of app. If None, queries every app.
    :param cursor: (Cursor) for custom queries. Default False to generate it based on the app
    :return: Creates .pkl
    """
    if not cursor:
        cursor = get_cursor(app)
    df = pd.DataFrame(columns=['app', 'item_name', 'date', 'median_sell_price', 'quantity'])
    for entry in cursor: # Need to manipulate the data in dict format one entry at a time, then concat into existing df
        split_col()
        strip_hours()
        remove_non_daily()
        transform_to_datetime()
    pickle_df(df, filename)




client = MongoClient()
db = client.steam_capstone
collection = db.market
cursor = collection.find({'app':578080})
df = pd.DataFrame(columns=['date', 'median_sell_price', 'quantity', 'app', 'item_name'])
a = cursor.next()

def transform(a):
    df2 = pd.DataFrame.from_dict(a['prices'])
    df2['app'] = a['app']
    df2['item_name'] = a['item_name']
    return df2

def get_dates(a): # Should be able to get a df from this with datetime, price, quant
    s = pd.Series(name='date')
    for i, x in enumerate(a['prices']):
        if len(s) > 0 and pd.to_datetime(x['date'][:11]) == s.iloc[-1]:
            break
        s = s.append(pd.Series(pd.to_datetime(x['date'][:11]), index=[i]))
    return s.iloc

def get_dates_prices_quants(a): # Concatenate all of these together
    df = pd.DataFrame(columns=['median_sell_price', 'quantity', 'date'])
    for i, x in enumerate(a['prices']):
        if len(df) > 0 and pd.to_datetime(x['date'][:11]) == df.date.iloc[-1]:
            break
        df = pd.concat([df, pd.DataFrame.from_dict(
            {'median_sell_price': [x['median_sell_price']],
             'quantity': [x['quantity']],
             'date': [pd.to_datetime(x['date'][:11])]})],ignore_index=True)
    df['app'] = a['app']
    df['item'] = a['item_name']
    return df


def iterator2dataframe(iterator,
                       chunk_size: int,
                       func=None,
                       **kwargs) -> pd.DataFrame:
    """Turn an Mongo iterator into multiple small pandas.DataFrame
    This is a balance between memory and efficiency
    If no result, return empty pandas.DataFrame
    Args:
      iterator: an iterator
      chunk_size: the row size of each small pandas.DataFrame
      func: generator to transform each record
      kwargs: extra parameters passed to tqdm.tqdm
    Returns:
      pandas.DataFrame
    """
    records = []
    frames = []
    for i, record in enumerate(tqdm(iterator, total=97636, **kwargs)):
        if func:
            for new_record in func(record):
                records.append(new_record)
        else:
            records.append(record)
        if i % chunk_size == chunk_size - 1:
            frames.append(pd.DataFrame(records))
            records = []
    if records:
        frames.append(pd.DataFrame(records))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


# func parameter example, must be a Generator
def record_result(record):
    last_date = 0
    for interaction in record['prices']:
        #date = pd.to_datetime(interaction['date'][:11])
        date = time.mktime(datetime.datetime.strptime(interaction['date'][:11], "%b %d %Y").timetuple())
        if date == last_date:
            break
        yield {
            'median_sell_price': interaction['median_sell_price'],
            'quantity': int(interaction['quantity']),
            'date': date,
            'app': record['app'],
            'item_name': record['item_name']}
        last_date = date


if __name__ == '__main__':
    client = MongoClient()
    db = client.steam_capstone
    collection = db.market
    with open('data/all_apps_df.pkl', 'wb') as f:
        pickle.dump(iterator2dataframe(collection.find(), 20, func=record_result), f)