import pickle
from pyculiarity import detect_ts
from pyramid.arima import auto_arima
from collections import defaultdict
import pandas as pd
from dendrogram_class import mask_mins
from tqdm import tqdm



def import_data():
    """
    Load in the dataframe and add the 'timestamp' converted date
    """
    with open('data/cs_df_M.pkl', 'rb') as f:
        df = pickle.load(f)
    return df


def filter_data(dataframe, min_price=.1, min_quant=30, days_released=30):
    """
    Filter items that don't meet the threshold of price or quantity. Remove the first few days of release where the
    price is always very high.
    :param dataframe: df
    :param min_price: (float) min price the item needs to be kept. Exclusive.
    :param min_quant: (int) min quantity the item needs to be kept. Exclusive.
    :param days_released: (int) Remove the first few days of release where the price is always very high.
    :return: df
    """
    df = mask_mins(dataframe, min_price, min_quant)
    df = df[df.days_since_release > days_released]
    return df


def anom_consensus(dataframe):
    """
    Given a price/quant/release_date filtered DataFrame, run anomaly detection on data that has been smoothed by
    auto arima
    :return: a list of (Timestamp, number of anomalies) sorted most anomalies to least
    """
    anom_dict = defaultdict(lambda: 0)
    items = dataframe.item_name.unique()
    for item in tqdm(items):
        df, release_date = prep_data(dataframe, item)
        results = arima_smooth(df)
        results = detect_anoms(results)
        anom_dict = update_anoms(anom_dict, results, release_date)
    return sort_dict(anom_dict)


def prep_data(dataframe, item):
    """
    Extract the time series for the given item, and return only the timestamp and median_sell_price columns to be used
    for detecting anomalies. Also returns the first timestamp, which is used to filter anomalies.
    :param dataframe: full dataframe
    :param item: Item name
    :return: DataFrame([timestamp, median_sell_price]), first timestamp
    """
    df = dataframe[dataframe['item_name'] == item]
    return df[['timestamp', 'median_sell_price']].reset_index(drop=True), df.iloc[0]['timestamp']


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
    :return:
    """
    if len(results.index)>0:
        for anomaly in results.index:
            if anomaly != release_date:
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



# if __name__ == '__main__':
#     df = import_data()
#     df = filter_data(df)
#     anomalies = anom_consensus(df)
#     with open('anomalies.pkl', 'wb') as f:
#         pickle.dump(anomalies, f)
#     print_top(anomalies, n=30)
