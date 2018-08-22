import numpy as np
import pandas as pd
from datetime import datetime
import time


def string_to_epoch(time_str, format='%d %b %Y'):
    return time.mktime(datetime.strptime(time_str, format).timetuple())

def string_to_Timestamp(time_str, format='%d %b %Y'):
    return epoch_to_Timestamp(string_to_epoch(time_str, format)) # inefficient

def string_to_np(time_str, format='%d %b %Y'):
    return epoch_to_np(string_to_epoch(time_str, format)) # inefficient

def epoch_to_string(time_float, format='%d %b %Y'):
    return datetime.fromtimestamp(time_float).strftime(format)

def epoch_to_Timestamp(time_float):
    return pd.to_datetime(time_float, unit='s')

def epoch_to_np(time_float):
    return np.datetime64(datetime.fromtimestamp(time_float).date())

def timestamp_to_string(timestamp, format='%d %b %Y'):
    return timestamp.date().strftime(format)

def timestamp_to_epoch(timestamp):
    return string_to_epoch(timestamp_to_string(timestamp)) # inefficient

def timestamp_to_np(timestamp):
    return string_to_np(timestamp_to_string(timestamp)) # inefficient

def np_to_string(time_np, format='%d %b %Y'):
    return timestamp_to_string(np_to_Timestamp(time_np), format) # inefficient

def np_to_epoch(time_np):
    return timestamp_to_epoch(np_to_Timestamp(time_np)) # inefficient

def np_to_Timestamp(time_np):
    return pd.Timestamp(time_np)
