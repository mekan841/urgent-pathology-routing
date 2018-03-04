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

class Trips():
    """Trips"""

    def __init__(self):

        self.BASE_DIR = ''
        self.INPUT_FILE = os.path.join(self.BASE_DIR, '/path/to/dataset_two_geocoded_cleaned.tsv')
        
        self.START_TIMESTAMP = 1487588400
        self.END_TIMESTAMP = 1498434900
        self.END_SIMULATION_TIMESTAMP = 1498392000

        self.START_DATE = 'YYYY-mm-dd'
        self.HUMAN_READABLE_END_TIME = 'Monday, January 01, 2018 00:00:00 AM GMT+12:00'

        self.mean_fare_for_address = {}
        self.simulated_trips_df = None

    def load_df(self):

        df = pd.read_csv(self.INPUT_FILE, header=0, index_col=0, sep='\t')
        dfraw = df.copy()

        df = dfraw.copy()
        df['Trans DateDT'] = pd.to_datetime(df['Trans Date'] + " " + df['Trans Time'], format='%d/%m/%Y %H:%M:%S')
        df = df[df['Trans DateDT'] >= pd.to_datetime(self.START_DATE, format='%Y-%m-%d')]
        df = df.sort_values(by='Trans DateDT')

        x = pd.DatetimeIndex(df['Trans DateDT'])
        y = x.tz_localize('Pacific/Auckland', ambiguous='NaT')

        df['Trans DateDT'] = y
        df = df[~df['Trans DateDT'].isnull()].copy()

        df['dt_value'] = [np.int64(x.value) for x in list(df['Trans DateDT'])]
        df['ts'] = (df.dt_value / 1e9).astype(int)
        
        self.df = df


    def learn_fare_for_address(self):

        self.mean_fare_for_address = {}
        for i in pd.Series.unique(self.df.formatted_address):
            f = np.median(self.df[self.df.formatted_address == i]['Fare excl'])
            self.mean_fare_for_address[i] = f


    def describe_dataframes(self):

        print('true data frame')
        print(self.df.groupby('formatted_address').agg({"dt_value":len}).sort_values(by='dt_value', ascending=False))
        print('\n'*5)
        print('boosted data frame')
        print(self.simulated_trips_df.groupby('formatted_address').agg({"dt_value":len}).sort_values(by='dt_value', ascending=False))



    def simulate_new_set_of_trips(self):

        from tick.base import TimeFunction
        from tick.hawkes import SimuInhomogeneousPoisson

        df = self.df
        df['hod'] = [r.hour for r in df['Trans DateDT']]
            
        rate_per_hour = df.groupby(['hod']).agg({"lat":len}).rename(columns={'lat': 'hourSum'})
        rate_per_hour['normalizedHourSum'] = rate_per_hour.hourSum / np.sum(rate_per_hour.hourSum)
        rate_per_hour['scaled_by_hours'] = rate_per_hour.normalizedHourSum / 125.53819444444444

        hour_to_base_rate_dict = rate_per_hour[['scaled_by_hours']].to_dict()['scaled_by_hours']
        base_rates = np.array(list(hour_to_base_rate_dict.values()))

        total_per_address = df.groupby(['formatted_address']).agg({"lat":len}).rename(columns={'lat': 'formatted_addressSum'})

        simulated_data = []
        print('Simulating...')
        c = 0
        addresses = pd.Series.unique(df.formatted_address)
        for add in addresses:
            c += 1
            total_per_address_i = 1000
            loc_base_rates = base_rates * total_per_address_i
            T = []
            Y = []
            hour_count = 0
            while hour_count < 3001 + 1:
                T.append(hour_count)
                Y.append(loc_base_rates[hour_count % 24])

                hour_count = hour_count + 1

            tf = TimeFunction((T, Y), dt=0.1)
            run_time = 3001
            in_poi = SimuInhomogeneousPoisson([tf], end_time=run_time, verbose=False)
            in_poi.track_intensity(0.1)
            in_poi.simulate()
            for h in in_poi.timestamps[0]:
                ts = self.START_TIMESTAMP + h * 3600
                simulated_data.append((add, ts, self.mean_fare_for_address[add]))

        self.simulated_trips_df = pd.DataFrame(simulated_data, columns=['formatted_address', 'ts', 'Fare excl'])
        self.simulated_trips_df = self.simulated_trips_df.sort_values(by='ts')
        self.simulated_trips_df['Trans DateDT'] = pd.to_datetime(self.simulated_trips_df['ts'], unit='s')

        x = pd.DatetimeIndex(self.simulated_trips_df['Trans DateDT'])
        y = x.tz_localize('UTC', ambiguous='NaT')
        y = y.tz_convert('Pacific/Auckland')

        self.simulated_trips_df['Trans DateDT'] = y
        self.simulated_trips_df = self.simulated_trips_df[~self.simulated_trips_df['Trans DateDT'].isnull()].copy()

        self.simulated_trips_df['dt_value'] = [np.int64(x.value) for x in list(self.simulated_trips_df['Trans DateDT'])]
        self.simulated_trips_df['ts_recalculated_for_check'] = self.simulated_trips_df.dt_value / 1e9

        self.simulated_trips_df['ts_recalculated_for_check'] = self.simulated_trips_df.ts_recalculated_for_check.astype(int)
        self.simulated_trips_df['ts'] = self.simulated_trips_df.ts.astype(int)



if __name__ == "__main__":

    t = Trips()
    t.load_df()
    t.learn_fare_for_address()
    t.simulate_new_set_of_trips()

