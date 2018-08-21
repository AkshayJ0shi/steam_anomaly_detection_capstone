from datetime import datetime
import time


def from_ts(ts):
    """ Converts epoch time to a readable date """
    return datetime.fromtimestamp(ts)

def to_ts(dt):
    """ Converts time of the form 'Jan 01 2020' to epoch time """
    return time.mktime(datetime.strptime(dt, "%b %d %Y").timetuple())


def to_timeseries(df, item=None):
    df = df[(df['item_name'] == item)]
    df['date'] = [datetime.fromtimestamp(t) for t in df['date']]
    df.index = df['date']
    return df.median_sell_price

def anomaly_format():
    pass

def anomaly_vec_format():
    pass

def arima_format():
    pass
