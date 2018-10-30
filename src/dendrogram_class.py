import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import StandardScaler
from src.date_util import str_to_float



class Dendrogram:
    def __init__(self):
        self.df = None
        self.pivot = None


    def fit(self, df):
        """
        Saves the df for queries and establishes a default pivoted df for the dendrogram. Run make_pivot() to change
        what is being clustered.
        """
        self.df = df
        self.make_pivot()


    def make_pivot(self, min_price=0.03, min_quant=40, days_dropped=100,
                   start_date='Jan 01 2017', end_date='Dec 31 2017', scale=False, total_days=None):
        """
        Makes a pivoted dataframe to be used in the dendrogram.
        :param min_price: (float) min price the item needs to be kept. Exclusive.
        :param min_quant: (int) min quantity the item needs to be kept. Exclusive.
        :param days_dropped: (int) number of days after the release date of the item to remove
        :param start_date: (timeseries or 'Jan 01 2020')
        :param end_date: (timeseries or 'Jan 01 2020')
        :param scale: (bool) whether or not to Standardize the data
        :param total_days: shifts the time serieses to line up on day released
        :return: a pivot of the fit df with the set of parameters
        """
        self.pivot = self.df.dropna() # make a copy and drop anything that does not have a release date (might remove)
        self.pivot = mask_mins(self.pivot, min_price, min_quant)
        self.pivot = self.pivot[self.pivot['days_since_release'] > days_dropped]
        # restrict the df to the specified date range
        if type(start_date) == str:
            self.pivot = self.pivot[[(x >= str_to_float(start_date, format='%b %d %Y')) \
                                     and (x <= str_to_float(end_date, format='%b %d %Y')) for x in self.pivot.date]]
        else:
            self.pivot = self.pivot[[(x >= start_date) and (x <= end_date) for x in self.pivot.date]]
        self.pivot['info'] = self.pivot['item_name'] + ' ' + self.pivot['release_date']
        self.pivot = self.pivot.reset_index().pivot('info', 'date', 'median_sell_price')
        self.pivot = self.pivot.dropna() # remove items that were not release for the full date range
        if scale:
            self.pivot = pd.DataFrame(StandardScaler().fit_transform(self.pivot.transpose()).T,
                                  index=self.pivot.index, columns=self.pivot.columns)


    def make_dendrogram(self, linkage_method='average', metric='cosine', save=False, color_threshold=None):
        make_dendrogram(self.pivot, linkage_method=linkage_method, metric=metric, save=save, color_threshold=color_threshold)


def mask_mins(dataframe, min_price=.15, min_quant=30, days_released=60):
    """
    Filter items that don't meet the threshold of price or quantity. Remove the first few days of release where the
    price is always very high.
    :param dataframe: df
    :param min_price: (float) min price the item needs to be kept. Exclusive.
    :param min_quant: (int) min quantity the item needs to be kept. Exclusive.
    :param days_released: (int) Remove the first few days of release where the price is always very high.
    :return: df
    """
    # find the minimum quantity and minimum price for each item
    df = dataframe.copy()
    df['min_quant'] = df.groupby('item_name')['quantity'].transform('min')
    df['min_price'] = df.groupby('item_name')['median_sell_price'].transform('min')
    # remove all items with price and quant < threshold
    df = df[df.min_quant > min_quant]
    df = df[df.min_price > min_price]
    #remove the first 'days_released' number of items
    return df[df.days_since_release > days_released]


def make_dendrogram(dataframe, linkage_method='average', metric='cosine', save=False, color_threshold=None):
    """
    Plot a dendrogram of standardized data with items as labels
    :param dataframe: standardized, pivoted dataframe
    :param linkage_method: linkage type for hierarchical clustering (default 'average')
    :param metric:
    :param save: (bool) save dendrogram as 'dendrogram.png'
    :param color_threshold:
    :return:
    """

    distxy = squareform(pdist(dataframe.values, metric=metric))
    Z = linkage(distxy, linkage_method)
    plt.figure(figsize=(25, 20))
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel('Items')
    plt.ylabel('Distance')
    dendrogram(
        Z,
        leaf_rotation=90.,  # rotates the x axis labels
        leaf_font_size=5,  # font size for the x axis labels
        labels=dataframe.index,
        color_threshold=color_threshold
    )
    if save:
        plt.gcf()
        plt.tight_layout()
        plt.savefig('dendrogram.png', dpi=400, pad_inches=0)
    plt.show()