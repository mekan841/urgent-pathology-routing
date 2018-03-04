
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

import matplotlib.pyplot as plt
import time
from sklearn.cluster import DBSCAN
from sklearn import metrics
import copy

class Benchmarks():
    """Benchmarks"""
    def __init__(self):
        pass

    def get_batching_costs(self, df):
        for xx in []: # addresses
            df = df[(df.formatted_address.str.contains(xx))]

            ## calculate the duration of existing trips using the origin-to-lab cache
            existing_durations = []
            for i, r in df.iterrows():
                existing_durations.append(origin_to_lab_times[r['formatted_address']])


            for input_allowable_delay_times in [(6,20),(6,40),(6,60)]:

                print(input_allowable_delay_times)

                master_trips = set()
                sub_trips = set()

                c = 0
                for i, r in df.iterrows(): #[~df.formatted_address.str.contains('401')]

                    # if c % 100 == 0:
                    #     print(c)
                    c += 1

                    if i in sub_trips:
                        continue

                    master_trips.add(i)
                    ts = np.int64(r['dt_value'])

                    trips_within_Xmin = df[(df['dt_value'] < ts + 5*60*1e9 + input_allowable_delay_times[1]*60*1e9) & (df['dt_value'] - ts > +0.1)]

                    if len(trips_within_Xmin) == 0:
                        continue
                    else:
                        for ii, rr in trips_within_Xmin.iterrows():
                            sub_trips.add(ii)

                print(len(sub_trips))
                print(len(master_trips))
                print(len(sub_trips) / (len(sub_trips) + len(master_trips)))
                print(len(sub_trips) / (7988))
                print(len(sub_trips) + len(master_trips) - len(master_trips))
                print(((len(df) - len(master_trips))*9.57)*365/126)
                print(((len(df) - len(master_trips))*9.57)/137806.06000001408)

                print('-'*100)

    def find_existing_durations_and_costs(self, df, distances):
        ## calculate the duration of existing trips using the origin-to-lab cache
        existing_durations = []
        for i, r in df.iterrows():
            existing_durations.append(distances.origin_to_lab_times[r['formatted_address']])
        print('existing durations', np.sum(existing_durations))
        print('existing costs', np.sum(df['Fare excl']))
