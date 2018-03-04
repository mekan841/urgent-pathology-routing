
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
import itertools

from trips import Trips as Trips
from distances import Distances as Distances
from scheduler_v2 import Scheduler

class Simulator():
    """Simulator"""

    def __init__(self, trips):
        self.trips = trips

    def open_outfile(self):
        self.outfile = open('path/to/tmp/log-' + str(int(time.time())) + '.txt', 'w')


    def simulation(self, source):

        self.trips = trips
        acceptable_delay = 20 * 60
        self.TIMESTEP = 1*60

        self.scheduler1 = Scheduler(acceptable_delay)
        self.scheduler2 = Scheduler(acceptable_delay)

        if source == 'real':
            df = self.trips.df[['formatted_address', 'ts', 'Fare excl']].copy().sort_values(by='ts')
        if source == 'simulated':
            df = self.trips.simulated_trips_df[['formatted_address', 'ts', 'Fare excl']].copy().sort_values(by='ts')
        
        ts = self.trips.START_TIMESTAMP
        
        self.master_trips = {}
        self.master_trips_durations = []
        self.sub_trips = {}

        c = 0
        length_1_trips = 0
        length_over_1_trips = 0
        while ts < self.trips.END_TIMESTAMP:
            if c % 1000 == 0 and c > 1:
                pass
            c += 1
            requests = df[(df.ts > (ts - self.TIMESTEP)) & (df.ts <= ts)]
            requests2 = []
            for i, r in requests.iterrows():
                t = {'id': i, 'formatted_address': r['formatted_address'], 'ts': r['ts'], 'Fare excl': r['Fare excl'], 'tsh': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(r['ts']))}
                requests2.append(t)

            self.scheduler1.add_to_buffer(requests2)
            self.scheduler2.add_to_buffer(requests2)

            trips1 = self.scheduler1.scheduler_decision_batching(ts)
            trips2 = self.scheduler2.scheduler_decision_combining(ts)

            ts = ts + self.TIMESTEP

        print(source + '\t' + 'current_time_ratios\t' + str(float(self.scheduler1.modified_durations) / float(self.scheduler1.unmodified_durations)) + '\t' + str(float(self.scheduler2.modified_durations) / float(self.scheduler2.unmodified_durations)))
        self.outfile.write(source + '\t' + 'current_time_ratios\t' + str(float(self.scheduler1.modified_durations) / float(self.scheduler1.unmodified_durations)) + '\t' + str(float(self.scheduler2.modified_durations) / float(self.scheduler2.unmodified_durations)) + '\n')

    def close_outfile(self):
        self.outfile.close()


trips = Trips()
trips.load_df()
trips.learn_fare_for_address()

s = Simulator(trips)
s.open_outfile()

s.simulation('real')

for i in range(50):
    
    trips.simulate_new_set_of_trips()
    s.simulation('simulated')

s.close_outfile()

