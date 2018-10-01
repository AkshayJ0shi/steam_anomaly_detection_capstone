import numpy as np
import pandas as pd
from datetime import datetime
import time
import re


def date_converter(date, convert_to='string', str_format=False):
    """
    Converts any datetime object into any other (that I've accounted for).
    :param date: any date objects listed below. String must be of the form '15 Jan 2001'
    :param convert_to: Options are 'string', 'float', 'datetime', 'datetime64' (numpy), 'timestamp' (pandas)
    :param str_format: Specify format if converting to string. Default will be '15 Mar 2001'. Must be specified
                       to convert from 'string'
    :return: Converted date type object
    """
    # str(type()) returns somethig like "<class 'pandas.Timestamp'>" and I want to extract 'Timestamp'
    if str_format and convert_to == 'string':
        return eval(re.findall(r'(\w+)', str(type(date)))[-1].lower() + '_to_string(date, format=str_format)')
    return eval(re.findall(r'(\w+)', str(type(date)))[-1].lower() + '_to_{}(date)'.format(convert_to))

# Need to rename functions, and replace them in other files with the date_converter.
# types are: datetime, datetime64 (numpy), timestamp (pandas), float, string

def string_to_float(time_str, format='%d %b %Y'):
    return time.mktime(datetime.strptime(time_str, format).timetuple())

def string_to_timestamp(time_str, format='%d %b %Y'):
    return float_to_timestamp(string_to_float(time_str, format))  # inefficient

def string_to_datetime64(time_str, format='%d %b %Y'):
    return float_to_datetime64(string_to_float(time_str, format))  # inefficient

def float_to_string(time_float, format='%d %b %Y'):
    return datetime.fromtimestamp(time_float).strftime(format)

def float_to_timestamp(time_float):
    return pd.to_datetime(time_float, unit='s')

def float_to_datetime64(time_float):
    return np.datetime64(datetime.fromtimestamp(time_float).date())

def timestamp_to_string(timestamp, format='%d %b %Y'):
    return timestamp.date().strftime(format)

def timestamp_to_float(timestamp):
    return string_to_float(timestamp_to_string(timestamp))  # inefficient

def timestamp_to_datetime64(timestamp):
    return string_to_datetime64(timestamp_to_string(timestamp))  # inefficient

def datetime64_to_string(time_np, format='%d %b %Y'):
    return timestamp_to_string(datetime64_to_timestamp(time_np), format) # inefficient

def datetime64_to_float(time_np):
    return timestamp_to_float(datetime64_to_timestamp(time_np))  # inefficient

def datetime64_to_timestamp(time_np):
    return pd.Timestamp(time_np)

def datetime_to_datetime64(date):
    return np.datetime64(date)

def datetime_to_timestamp(date):
    return pd.Timestamp(date)

def datetime_to_float(date):
    return date.timestamp()

def datetime_to_string(date, format='%d %b %Y'):
    return date.strftime(format)

def string_to_datetime(date, format='%d %b %Y'):
    return datetime.strptime(date, format)

def float_to_datetime(date):
    return datetime.fromtimestamp(date)

def datetime64_to_datetime(date):
    return pd.Timestamp(date).to_pydatetime()

def timestamp_to_datetime(date):
    return date.to_pydatetime()


