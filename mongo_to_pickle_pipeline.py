from pymongo import MongoClient
import pandas as pd
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

# Code borrowed from http://deo.im/2016/09/22/Load-data-from-mongodb-to-Pandas-DataFrame/
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
    for i, record in enumerate(tqdm(iterator, **kwargs)):
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
def split_sales_records(record):
    """
    For each item, makes each date/price/quantity separate rows
    :param record:
    :return:
    """
    for interaction in record['prices']:
        # date = pd.to_datetime(interaction['date'][:11]) # <- took up too much memory (I think)
        date = time.mktime(datetime.datetime.strptime(interaction['date'][:11], "%b %d %Y").timetuple())
        if date > 1.530335e+09: # This will occur when we go from daily records to hourly. Just taking records before Jul 01 2018
            break
        yield {
            'median_sell_price': interaction['median_sell_price'],
            'quantity': int(interaction['quantity']),
            'date': date,
            'app': record['app'],
            'item_name': record['item_name']}

# Commented out to avoid overwritting
# if __name__ == '__main__':
#     cursor = get_cursor()
#     df = iterator2dataframe(cursor, 20, func=split_sales_records, total=cursor.count())
#     with open('data/all_apps_df.pkl', 'wb') as f:
#         pickle.dump(df, f)