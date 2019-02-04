import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates



def fromts(ts):
    """ Converts epoch time to a readable date """
    return datetime.datetime.fromtimestamp(ts)

def tots(dt):
    """ Converts time of the form 'Jan 01 2020' to epoch time """
    return time.mktime(datetime.datetime.strptime(dt, "%b %d %Y").timetuple())

def fit_moving_average_trend(series, window=7):
    """ Create a series of moving averages """
    return series.rolling(window, center=True).mean()

def plot_raw(series, ax, title='Raw'):
    plt.style.use('ggplot')
    months = mdates.MonthLocator()
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.plot(series.index, series.values)
    ax.set_title(title)
    plt.show()

def plot_moving_average(series, ax, title="Item", window=30, draw_raw=True):
    """
    Plots a moving average over the original plot.
    :param series:
    :param ax: axis to plot on
    :param title: plot title (default: item name)
    :param window: (int) moving average window size (default: 7 days)
    :param draw_raw: (bool) whether or not to plot raw data (default: True)
    :return:
    """
    plt.style.use('ggplot')
    months = mdates.MonthLocator()
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.style.use('ggplot')
    if draw_raw:
        ax.plot(series.index, series.values)
    ax.plot(series.index, fit_moving_average_trend(series, window), c='b')
    ax.set_title(title + ' Moving Average (' + str(window) + ' days)')
    plt.show()

def plot_resid(series, ax, title='Residual', window=7):
    plt.style.use('ggplot')
    months = mdates.MonthLocator()
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.plot(series.index, fit_moving_average_trend(series, window).values - series.values)
    ax.set_title(title + ' Residual Plot')
    plt.show()
