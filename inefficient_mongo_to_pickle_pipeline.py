from pymongo import MongoClient
import pickle
import pandas as pd
import numpy as np


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


def mongo_to_df(cursor):
    """
    Loads the data from a Cursor into a df
    :return:
    """
    return pd.DataFrame(list(cursor))


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


def transform_to_datetime(df):
    """
    Transforms the formatted date to a datetime object
    :param df:
    :return:
    """
    df.date = pd.to_datetime(df.date)
    return df


def pickle_df(df, filename):
    """
    Saves the df into a pickle
    :param df: clean df
    :param filename: (str) name of .pkl file
    :return:
    """
    with open(filename + '.pkl', 'wb') as f:
        pickle.dump(df, f)



def mongo_to_clean_df_pipeline(filename, app=None):
    """
    Creates pickle file of a cleaned dataframe
    :param filename: (str) name of pickle file
    :param app: (int) id of app
    :return:
    """
    cursor = get_cursor(app)
    df = mongo_to_df(cursor)
    df = split_col(df)
    df = strip_hours(df)
    df = remove_non_daily(df)
    df = transform_to_datetime(df)
    df = df.drop(columns='_id')
    pickle_df(df, filename)
    pass


if __name__ == '__main__':
    mongo_to_clean_df_pipeline('data/dota2_df', app=570)
    mongo_to_clean_df_pipeline('data/tf2_df', app=440)
    mongo_to_clean_df_pipeline('data/csgo_df', app=730)
    mongo_to_clean_df_pipeline('data/full_df')