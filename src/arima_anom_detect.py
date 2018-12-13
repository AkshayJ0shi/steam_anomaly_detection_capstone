import pickle
from pyculiarity import detect_ts
from pyramid.arima import auto_arima
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm



def import_data(guns_only=False):
    """
    Load in the dataframe and add the 'timestamp' converted date
    """
    with open('data/cs_df_M.pkl', 'rb') as f:
        df = pickle.load(f)
    if guns_only:
        return df[df['gun_bool']]
    return df


# update with df.groupby().filter()
def filter_data(dataframe, min_price=.15, min_quant=30, days_released=45):
    """
    Filter items that don't meet the threshold of price or quantity. Remove the first few days of release where the
    price is always very high.
    :param dataframe: df
    :param min_price: (float) min price the item needs to be kept. Exclusive.
    :param min_quant: (int) min quantity the item needs to be kept. Exclusive.
    :param days_released: (int) Remove the first few days of release where the price is always very high.
    :return: df
    """
    # remove the first 'days_released' number of items
    df = dataframe[dataframe.days_since_release > days_released]
    # find the minimum quantity and minimum price for each item
    df['min_quant'] = df.groupby('item_name')['quantity'].transform('min')
    df['min_price'] = df.groupby('item_name')['median_sell_price'].transform('min')
    # remove all items with price and quant < threshold
    df = df[df.min_quant > min_quant]
    return df[df.min_price > min_price]


def anom_consensus(dataframe, arima=True):
    """
    Given a price/quant/release_date filtered DataFrame, run anomaly detection on data that has been smoothed by
    auto arima
    :return: a list of (Timestamp, number of anomalies) sorted most anomalies to least
    """
    anom_dict = defaultdict(lambda: 0)
    for item, df in tqdm(dataframe.groupby('item_name'), miniters=1):
        df, release_date = prep_data(df)
        if arima:
            results = arima_smooth(df)
        else:
            results = df[['timestamp', 'median_sell_price']]
            results.columns = ['timestamp', 'pred_price']
        results = detect_anoms(results)
        anom_dict = update_anoms(anom_dict, results, release_date)
    anoms = sort_dict(anom_dict)
    return scale_anomalies(anoms, dataframe)


def prep_data(dataframe):
    """
    Extract the time series for the given item, and return only the timestamp and median_sell_price columns to be used
    for detecting anomalies. Also returns the first timestamp, which is used to filter anomalies.
    :param dataframe: dataframe of one item (groupby item_name)
    :return: DataFrame([timestamp, median_sell_price]), first timestamp
    """
    return dataframe[['timestamp', 'median_sell_price']].reset_index(drop=True), dataframe.iloc[0]['timestamp']


def arima_smooth(df):
    """
    Find best arima and predict the prices with that model. If no model is fit, returns the original.
    :param df:
    :return: smoothed timeseries with columns ['timestamp', 'pred_prices']
    """
    arima = auto_arima(df['median_sell_price'], error_action="ignore", suppress_warnings=True, m=4)
    # if arima does not converge, return the original df
    if arima is None:
        result = df[['timestamp', 'median_sell_price']]
        result.columns = ['timestamp', 'pred_price']
        return result
    return pd.DataFrame({'timestamp':df.iloc[1:]['timestamp'], 'pred_price': arima.predict_in_sample(start=1)})


def detect_anoms(dataframe):
    """
    Run anomaly detection.
    :param dataframe: dataframe with 'timestamp' and 'pred_price' columns
    :return: list of timestamps
    """
    df = dataframe[['timestamp', 'pred_price']].reset_index(drop=True)
    results = detect_ts(df, max_anoms=0.3, alpha=0.001, direction='both', only_last=None,
                     longterm=True, verbose=True, piecewise_median_period_weeks=3)
    return results['anoms']


def update_anoms(anom_dict, results, release_date):
    """
    Add 1 to each returned timestamp key in the anomaly dictionary
    :param anom_dict: current diction of {timestamp: number of anomalies}
    :param results: timestamps to update the anom_dict with
    :param release_date: First date of sale often comes back with an anomaly so I want to filter those.
    :return: updated dictionary
    """
    if len(results.index)>0:
        for anomaly in results.index:
            if anomaly != release_date:
                # possibly update with functionality that gives more weight to anomalies with larger quantity
                # anom_dict[anomaly] += temp_df[[datetime.datetime.fromtimestamp(t) == anomaly for t in temp_df.date]].quantity.values[0]
                anom_dict[anomaly] += 1
    return anom_dict


def sort_dict(anom_dict):
    """
    Sort the dictionary of {timestamp: anomaly count} by anomaly count
    """
    return sorted(anom_dict.items(), key=lambda x: x[1], reverse=True)


def print_top(anoms, n=30, sortByDate=False):
    """
    Print the n most common anomaly dates in a nice format

    """
    if sortByDate:
        print(*[(x.date().strftime('%d %b %Y'), y) for x, y in sorted(anoms[:n])], sep='\n')
    else:
        print(*[(x.date().strftime('%d %b %Y'), y) for x, y in anoms[:n]], sep='\n')


def get_num_items_per_day(df):
    """
        Creates a dataframe with 'release_timestamp' and 'total_released'.
        Use items_available(timestamp, df) with the returned df to get the number of items available for sale on that date.
        :return: df
    """
    num_items_df = Counter(df.groupby('item_name')['timestamp'].min().values)
    num_items_df = pd.DataFrame([(x, y) for x, y in num_items_df.items()],
                                columns=['release_timestamp', 'total_released'])
    num_items_df = num_items_df.sort_values('release_timestamp').reset_index(drop=True)
    num_items_df['total_released'] = np.cumsum(num_items_df['total_released'])
    return num_items_df


def items_available(ts, num_items_df):
    """
    Returns number of items available on a given day, with the given num_items_df (output of get_num_items_per_day(df))
    """
    return np.max(num_items_df[num_items_df['release_timestamp'] <= ts]['total_released'])


def scale_anomalies(anomalies, df):
    """
    Take the number of items available for sale on a given date into account. The magnitude of anomalies in 2018 will
    necessarily be larger than 2014, because there are more items. This divides the count of anomalies by the number
    of items available on that date to get a more accurate anomaly score.
    :param anomalies: list of anomalies
    :return: list of anomalies with scaled scores
    """
    num_items = get_num_items_per_day(df)
    scaled_anom_dict = {}
    for ts, count in anomalies:
        scaled_anom_dict[ts] = count / items_available(ts, num_items)
    return sort_dict(scaled_anom_dict)


def run_detection(filename, dataframe=pd.DataFrame(), guns_only=False,
                  min_price=.15, min_quant=30, days_released=45, arima=True):
    """
    Make it easy to run in one line without forgetting to filter or change the filename.
    :param filename: name of pickle file that will be saved
    :param dataframe: the string 'default' or a dataframe object. The dataframe object requires the following columns:
    'item_name', 'quantity', 'median_sell_price',
    :param guns_only: <bool> whether to take all items into account, or just the guns
    :param min_price: minimum price threshold for removing data
    :param min_quant: minimum quantity threshold for removing data
    :param days_released: number of days at the start of the time series to remove. Items almost universally sell for
    many times more than they do several days later
    :param arima: <bool> smooth with arima or not
    :return: list of (date, anomaly factor)'s sorted by anomaly factor
    """
    if dataframe.empty:
        df = import_data(guns_only=guns_only)
    else:
        df = dataframe
    df = filter_data(df, min_price=min_price, min_quant=min_quant, days_released=days_released)
    anomalies = anom_consensus(df, arima=arima)
    with open(filename, 'wb') as f:
        pickle.dump(anomalies, f)
    return anomalies


# This and some of the other filtering functions should probably be in a separate file
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
###############


# if __name__ == '__main__':
#     print_top(run_detection('anomalies.pkl'), n=30)
