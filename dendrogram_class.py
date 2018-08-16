import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist, squareform
from sklearn.preprocessing import StandardScaler
from ts_format import to_ts, from_ts


class Dendrogram():
    def __init__(self):

    def make_dendrogram(dataframe, linkage_method='average', metric='cosine', save=False, color_threshold=None):
        '''
        This function creates and plots the dendrogram created by hierarchical clustering.

        INPUTS: Pandas Dataframe, string, string, int

        OUTPUTS: None
        '''
        df_standard = StandardScaler().fit_transform(dataframe.transpose()).T
        distxy = squareform(pdist(df_standard.values, metric=metric))
        Z = linkage(distxy, linkage_method)
        plt.figure(figsize=(25, 10))
        plt.title('Hierarchical Clustering Dendrogram')
        plt.xlabel('sample index')
        plt.ylabel('distance')
        dendrogram(
            Z,
            leaf_rotation=90.,  # rotates the x axis labels
            leaf_font_size=6,  # font size for the x axis labels
            labels=dataframe.index,
            color_threshold=color_threshold
        )
        plt.show()
        if save:
            plt.gcf()
            plt.tight_layout()
            plt.savefig('dendogram', dpi=400, pad_inches=0)


    def make_pivot(dataframe, min_price, min_quant, days_dropped, start_date, end_date):
        """
        Makes a pivoted dataframe to be used in the dendrogram.
        :param dataframe: data
        :param min_price: (float) min price the item needs to be kept. Exclusive.
        :param min_quant: (int) min quantity the item needs to be kept. Exclusive.
        :param days_dropped: (int) number of days after the release date of the item to remove
        :param start_date: (timeseries or 'Jan 01 2020')
        :param end_date: (timeseries or 'Jan 01 2020')
        :return: a pivot of
        """
        df = dataframe.dropna() # make a copy and drop anything that does not have a release date (might remove)
        # find the minimum quantity and minimum price for each item
        df['min_quant'] = df.groupby('item_name')['quantity'].transform('min')
        df['min_price'] = df.groupby('item_name')['median_sell_price'].transform('min')

        # remove all items with price <
        df = df[df.min_quant > min_quant]
        df = df[df.min_price > min_price]

        df['item_index'] = np.nan
        df['item_index'] = df.groupby('item_name').transform(lambda x: np.arange(len(x)))
        df = df[df['item_index'] > days_dropped]

        df['num_sale_dates'] = df.groupby('item_name')['item_index'].transform('max')
        if type(start_date) == float:
            df_dates = df[[(x >= to_ts(start_date)) and (x <= to_ts(end_date)) for x in df.date]]
        else:
            df_dates = df[[(x >= start_date) and (x <= end_date) for x in df.date]]
        df_dates['info'] = df_dates['item_name'] + ' ' + df_dates['release_date']

        df_pivot = df_dates.reset_index().pivot('info', 'date', 'median_sell_price')

        return df_pivot.dropna()


    def mask_mins(min_price, min_quant)