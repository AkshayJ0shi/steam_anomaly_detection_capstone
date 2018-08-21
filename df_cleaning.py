import numpy as np
import pandas as pd
from datetime import datetime


def remove_low_quant(df):
    """
    Removes items that don't meet a threshold of quantity sold
    :param df: dataframe
    :return: copy of df
    """
    pass

def remove_non_daily(original_df):
    """
    Removes items that were not sold every day since they were released. I want consistant time series deltas. It is
    unlikely that any items would make the cut from remove_low_quantity but not be sold every day.
    :param original_df: dataframe
    :return: copy of original_df without items that were not sold every day
    """
    df = original_df.copy()
    df['date'] = [np.datetime64(datetime.fromtimestamp(t).date()) for t in df['date']]
    df['date_diff'] = df.groupby('item_name')['date'].diff()
    df['max_diff'] = df.groupby('item_name')['date_diff'].transform('max')
    return original_df[df.max_diff == pd.Timedelta('1 days 00:00:00')]

def remove_early_sales():
    pass