from random import sample
from src.anomaly_pipeline import *


def _test_fit_anom_from_db():
    """
    Test version of fit_anom_from_db using a small subset of the items.
    :return: print top 10 anomalies for now
    """
    terminal_display('Creating DataFrame...')
    with open('data/sql_db.pkl', 'rb') as f:
        df = pickle.load(f)
    df.columns = ['item_id', 'item_name', 'timestamp', 'median_sell_price', 'quantity']
    df = df.drop(columns=['item_id'])
    keep_items = sample(set(df[_test_mask_filters(df)].item_name.unique()), k=10)
    drop_items = sample(set(df[~_test_mask_filters(df)].item_name.unique()), k=10)
    query_items = keep_items + drop_items
    df = df[[x in query_items for x in df.item_name]]
    df['days_since_release'] = df.groupby('item_name')['timestamp']\
        .transform(lambda x: map(lambda y: y.days, x-min(x)))
    terminal_display('Beginning anomaly detection...')
    print_top(run_detection('anoms_from_db.pkl', dataframe=df), n=10)

def _test_fit_anom_sql(min_price=.15, min_quant=30, days_released=45):
    """
    Test version of fit_anom_sql using a small subset of the items.
    :return: print top 10 anomalies for now
    """
    terminal_display('Creating DataFrame...')
    conn = pg2.connect(dbname='steam_capstone', host='localhost')
    query = (
        """
        select t_days_released.item_name, t_days_released.date as timestamp, t_days_released.price as median_sell_price 
        from (select *, count(*) over (partition by item_name order by date asc) as days_released from sales) as t_days_released
        inner join (select item_name 
                    from (select *, count(*) over (partition by item_name order by date asc) as days_released from sales) as t 
                    where days_released > %(days_released)s 
                    group by item_name 
                    having min(price) > %(min_price)s and min(quantity) > %(min_quant)s) as t_keep_items
        on t_days_released.item_name = t_keep_items.item_name
        where days_released > %(days_released)s
        order by t_days_released.item_name, timestamp;
        """)
    df = sqlio.read_sql_query(query, conn, parse_dates=['timestamp'],
                              params={'min_price': min_price, 'min_quant': min_quant+1, 'days_released': days_released})
    keep_items = sample(set(df.item_name.unique()), k=10)
    df = df[[x in keep_items for x in df.item_name]]
    terminal_display('Beginning anomaly detection...')
    print_top(anom_consensus(df), n=10)


def _store_sql_db():
    conn = pg2.connect(dbname='steam_capstone', host='localhost')
    query = 'select * from sales order by item_name, date;'
    df = sqlio.read_sql_query(query, conn, parse_dates=['date'])
    with open('data/sql_db.pkl', 'wb') as f:
        pickle.dump(df, f)

def _test_mask_filters(dataframe, min_price=.15, min_quant=30):
    """
    Used in test_fit_anom_from_db. Gives a mask of data that meets the threshold requirements
    """
    df = dataframe.copy()
    df['min_quant'] = df.groupby('item_name')['quantity'].transform('min')
    df['min_price'] = df.groupby('item_name')['median_sell_price'].transform('min')
    # remove all items with price and quant < threshold
    return (df.min_quant > min_quant) & (df.min_price > min_price)

if __name__ == '__main__':
    update_database(update_date=datetime(2018, 11, 10).date())  # using manual date to avoid the 2 hour wait while it
                                                                # updates a couple of data points
    # if not os.path.isfile('data/sql_db.pkl'):
    #     _store_sql_db()
    # _test_fit_anom_from_db()
    _test_fit_anom_sql()