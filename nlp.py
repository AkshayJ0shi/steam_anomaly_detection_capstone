from pymongo import MongoClient
import pandas as pd
import numpy as np
import pickle
import re
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


def get_gun_patch_count():
    """
    Returns a list of tuples: [(num_documents, gun)...] where num_documents is a count of the number of patch notes the
    gun name appears in
    :return:
    """
    client = MongoClient()
    db = client['steam_capstone']
    collection = db['patches']
    with open('data/cs_df_M.pkl', 'rb') as f:
        df = pickle.load(f)
    guns = df.gun_type.dropna().unique()
    return sorted([(x, collection.count_documents({'patch_notes': {'$regex': x}})) for x in guns],
                  key=lambda x: x[1], reverse=True)

def stem_patch(patch):
    """Given the string of a patch update, tokenize and stem the patch notes"""
    patch = patch.lower()
    patch = [x for x in re.findall(r'(?!\d)[\w]+', patch)]
    patch = [x for x in patch if x not in stopwords.words()]
    stemmer = PorterStemmer()
    return [stemmer.stem(words) for words in patch]

def flatten(nested_list):
    """Break down list of lists into list of items"""
    return [item for sublist in nested_list for item in sublist]

def label_anom_patches(patch_dict, anom_dates):
    """
    Given a dict of {date:patch}, return [(notes, 0), (notes, 1)...]
    where index 1 labels anomalous or not.
    """
    anom_date_range = set(flatten([pd.date_range(date-pd.Timedelta(3, unit='D'), date+pd.Timedelta(3, unit='D'))
                                   for date in anom_dates]))
    return [(text, 1) if date in anom_date_range else (text, 0) for date, text in patch_dict.items()]