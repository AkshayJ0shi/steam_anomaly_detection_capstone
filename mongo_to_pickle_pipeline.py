from pymongo import MongoClient
import pickle
import pandas as pd
import numpy as np
import datetime


def mongo_to_df(cursor):
    """
    Loads the data from a Cursor into a df
    :return:
    """
    return pd.DataFrame(list(cursor))


def split_col(df, lst_col='prices'):
    return pd.DataFrame({col: np.repeat(df[col].values, df[lst_col].str.len())
                         for col in df.columns.difference([lst_col])}) \
             .assign(**{lst_col: np.concatenate(df[lst_col].values)})[df.columns.tolist()]


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
    Removes all entries that are not daily median/price data points.
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
    pass


def pickle_df():
    """
    Saves a pickle of the cleaned df
    :return:
    """
    pass


def get_cursor(app=False):
    client = MongoClient()
    db = client.steam_capstone
    collection = db.market
    if app:
        return pd.DataFrame(list(collection.find({'app': app})))
    else:
        return pd.DataFrame(list(collection.find()))


def mongo_to_clean_df_pipeline():
    pass


if __name__ == '__main__':
