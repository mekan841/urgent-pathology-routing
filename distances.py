
import sys
import os
import re
import json
import numpy as np
import pandas as pd
from datetime import datetime
import random
import itertools
import math
from collections import defaultdict
from collections import Counter
import time
import copy

from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import LabelEncoder

class Distances():
    """
    Contains estimated and/or learned estimates of the travel times between locations
    """

    def fit_regression_model(self):

        print(self.nzmg_dm_df.head())

    def __init__(self):

        self.origin_to_lab_times = {}
        self.origin_to_origin_times = {}
        self.origin_to_lab_distances = {}

        self.BASE_DIR = ''
        self.NZMG = os.path.join(self.BASE_DIR, 'fomatted_address_NZMG_from_mean_WGS84_coords_and_LINZ_website_with_id.csv')
        self.NZMG_DM_DF = os.path.join(self.BASE_DIR, 'fomatted_address_NZMG_from_mean_WGS84_coords_and_LINZ_website_with_id_distance_matrix.csv')
        self.LABORATORY_ADDRESS = '<address_here>'

        nzmg = pd.read_csv(self.NZMG, header=0, index_col=False)
        nzmg_dm_df = pd.read_csv(self.NZMG_DM_DF, header=0, index_col=False)

        for i in pd.Series.unique(nzmg.formatted_address):
            df_origin_to_lab = nzmg_dm_df[(nzmg_dm_df.origin_address == i) & (nzmg_dm_df.destination_address == self.LABORATORY_ADDRESS)]
            assert(len(df_origin_to_lab) == 1)
            self.origin_to_lab_times[i] = df_origin_to_lab.iloc[0].duration_in_traffic
            self.origin_to_lab_distances[i] = df_origin_to_lab.iloc[0].distance

        for i, r in nzmg_dm_df.iterrows():
            if r['origin_address'] == r['destination_address']:
                self.origin_to_origin_times[(r['origin_address'], r['destination_address'])] = 0    
            else:
                self.origin_to_origin_times[(r['origin_address'], r['destination_address'])] = r['duration_in_traffic']

        self.nzmg_dm_df = nzmg_dm_df
        self.nzmg = nzmg


class DistancesNov():

    def __init__(self):
        pass

    def fit_regression_model(self):

        df = pd.read_csv('/path/to/dataset_one.csv')
        df['start'] = pd.to_datetime(df['BookingDate'] + " " + df['MeterOnTime'], format='%d/%m/%Y %H:%M:%S')
        df['end'] = pd.to_datetime(df['BookingDate'] + " " + df['MeterOffTime'], format='%d/%m/%Y %H:%M:%S')
        df['hod'] = [r.hour for r in df['start']]
        df['hod'] = df['hod'].astype(int)
        df['duration'] = df.end - df.start
        df['duration'] = (df.duration.values / 1e9).astype(float) / 60
        df = df[df.duration > 0].copy()

        data = np.hstack((pd.get_dummies(df.PUAddress).values, pd.get_dummies(df.hod).values))
        y = np.array(df.duration)

        from sklearn import linear_model
        lr = linear_model.LinearRegression(fit_intercept=False)

        lr.fit(data, y)
        test = np.hstack((1*np.array(pd.get_dummies(df.PUAddress).columns == '<address_here>'), 1*np.array(pd.get_dummies(df.hod).columns == 12))).reshape(1,-1)
        print(lr.predict(test))

        df[(df.PUAddress == '<address_here>') & (df.duration > 0) & (df.hod == 12)][['hod','duration']].sort_values(by='hod').duration.mean()

if __name__ == "__main__":
    
    d = DistancesNov()
    d.run()




