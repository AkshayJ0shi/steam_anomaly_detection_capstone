import numpy as np
import pandas as pd
import datetime
import time


def string_to_epoch(time_str, format='%d %b %Y'):
    return time.mktime(datetime.datetime.strptime(time_str, format).timetuple())

def string_to_Timestamp(time_str, format='%d %b %Y'):
    return epoch_to_Timestamp(string_to_epoch(time_str, format))

def string_to_np(time_str, format='%d %b %Y'):
    return epoch_to_np(string_to_epoch(time_str, format))

def epoch_to_string(time_float, format='%d %b %Y'):
    return datetime.datetime.fromtimestamp(time_float).strftime(format)

def epoch_to_Timestamp(time_float):
    return pd.to_datetime(time_float, unit='s')

def epoch_to_np(time_float):
    return np.datetime64(datetime.datetime.fromtimestamp(time_float).date())

def timestamp_to_string(timestamp, format='%d %b %Y'):
    return timestamp.date().strftime(format)

# I haven't needed to make these conversions yet, but I left the stubs for later
def timestamp_to_epoch(timestamp):
    pass

def timestamp_to_np(timestamp):
    pass

def np_to_string(time_np):
    pass

def np_to_epoch(time_np):
    pass

def np_to_Timestamp(time_np):
    pass

