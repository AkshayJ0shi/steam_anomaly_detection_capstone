import datetime


def to_timeseries(df, item=None):
    df = df[(df['item_name'] == item)]
    df['date'] = [datetime.datetime.fromtimestamp(t) for t in df['date']]
    df.index = df['date']
    return df.median_sell_price