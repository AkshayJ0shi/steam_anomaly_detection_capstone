import datetime


def to_timeseries(df, item=None):
    df = df[(df['item_name'] == item)]
    df['date'] = [datetime.datetime.fromtimestamp(t) for t in df['date']]
    df.index = df['date']
    return df.median_sell_price

def anomaly_format():
    pass

def anomaly_vec_format():
    pass

def arima_format():
    pass
