
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



class Scheduler():

    def __init__(self, acceptable_delay):
        self.buffer = dict()
        self.distances = Distances()

        # acceptable delay is in seconds
        self.acceptable_delay = acceptable_delay

        self.buffer_counter = 0
        self.trips_out_counter = 0
        self.extra_trips_combined = 0

        self.unmodified_durations = 0
        self.modified_durations = 0

        self.requests_assigned = {}


    def add_to_buffer(self, transport_requests):
        
        if transport_requests is not None and len(transport_requests) != 0:
            for tr in transport_requests: 
                tr['must_send_taxi_time'] = tr['ts'] + self.acceptable_delay
                self.buffer[tr['id']] = tr
                tr['duration'] = self.distances.origin_to_lab_times[tr['formatted_address']]
                self.unmodified_durations += tr['duration']
                self.buffer_counter += 1

        self.number_of_transport_requests_in_buffer = len(self.buffer)
        
        self.locations_to_transport_requests_in_buffer = defaultdict(list)        
        for tr in self.buffer.values():
            self.locations_to_transport_requests_in_buffer[tr['formatted_address']].append(tr)
        
    def update_buffer(self, transport_requests):

        self.buffer = {}

        if transport_requests is not None and len(transport_requests) != 0:
            for tr in transport_requests: 
                self.buffer[tr['id']] = tr
                self.buffer_counter += 1

        self.number_of_transport_requests_in_buffer = len(self.buffer)
        
        self.locations_to_transport_requests_in_buffer = defaultdict(list)        
        for tr in self.buffer.values():
            self.locations_to_transport_requests_in_buffer[tr['formatted_address']].append(tr)


    def scheduler_decision_batching(self, ts):

        trips_to_return = []

        transport_requests_to_do_immediately = {}
        transport_requests_to_do_immediately_accounted_for = {}
        for tr in self.buffer.values():
            if ts > tr['must_send_taxi_time']:
                transport_requests_to_do_immediately[tr['id']] = tr

        for address in set([tr['formatted_address'] for tr in transport_requests_to_do_immediately.values()]):
            if len(self.locations_to_transport_requests_in_buffer[address]) > 1:
                trips_to_return.append([tr for tr in self.locations_to_transport_requests_in_buffer[address]])
                for tr in trips_to_return[-1]:
                    transport_requests_to_do_immediately_accounted_for[tr['id']] = tr

        for tr in transport_requests_to_do_immediately.values():
            if tr['id'] not in transport_requests_to_do_immediately_accounted_for:
                trips_to_return.append([tr])



        transport_requests_in_trips_to_return = {}
        for trip in trips_to_return:
            for tr in trip:
                transport_requests_in_trips_to_return[tr['id']] = 1 
        temp = []
        for tr in self.buffer.values():
            if tr['id'] not in transport_requests_in_trips_to_return:
                temp.append(tr)
        
        self.update_buffer(temp)

        duration = 0
        for x in trips_to_return:
            if len(x) == 1:
                duration += self.distances.origin_to_lab_times[x[0]['formatted_address']]
                self.trips_out_counter += 1
            else:
                duration += self.distances.origin_to_lab_times[x[0]['formatted_address']] 
                self.trips_out_counter += 1

        self.modified_durations += duration

        return trips_to_return



    def scheduler_decision_combining(self, ts):

        trips_to_return = []

        transport_requests_to_do_immediately = {}
        transport_requests_to_do_immediately_accounted_for = {}
        for tr in self.buffer.values():
            if ts > tr['must_send_taxi_time']:
                transport_requests_to_do_immediately[tr['id']] = tr

        locations_to_combine = []
        addresses = self.locations_to_transport_requests_in_buffer.keys()
        if len(addresses) >= 2:
            for x, y in itertools.combinations(addresses, 2):
                
                individual_times = self.distances.origin_to_lab_times[x] + self.distances.origin_to_lab_times[y]
                combined_times = self.distances.origin_to_origin_times[x, y] + min(self.distances.origin_to_lab_times[x], self.distances.origin_to_lab_times[y])
                if combined_times < individual_times:
                    locations_to_combine.append((x, y))


        for address in set([tr['formatted_address'] for tr in transport_requests_to_do_immediately.values()]):
            if len(self.locations_to_transport_requests_in_buffer[address]) > 1:
                trips_to_return.append(self.locations_to_transport_requests_in_buffer[address])
                for tr in trips_to_return[-1]:
                    transport_requests_to_do_immediately_accounted_for[tr['id']] = tr

                flag = 0
                for address_secondary in addresses:
                    if address_secondary == address:
                        continue
                    if (address_secondary, address) in locations_to_combine or (address, address_secondary) in locations_to_combine:
                        for tr in self.locations_to_transport_requests_in_buffer[address_secondary]:
                            trips_to_return[-1].append(tr)
                            transport_requests_to_do_immediately_accounted_for[tr['id']] = tr
                            flag = 1
                    if flag == 1:
                        break

        for tr in transport_requests_to_do_immediately.values():
            if tr['id'] not in transport_requests_to_do_immediately_accounted_for:
                trips_to_return.append([tr])

        transport_requests_in_trips_to_return = {}
        for trip in trips_to_return:
            for tr in trip:
                transport_requests_in_trips_to_return[tr['id']] = 1 
        temp = []
        for tr in self.buffer.values():
            if tr['id'] not in transport_requests_in_trips_to_return:
                temp.append(tr)
        
        self.update_buffer(temp)

        duration = 0
        for x in trips_to_return:
            if len(x) == 1:
                duration += self.distances.origin_to_lab_times[x[0]['formatted_address']]
                self.trips_out_counter += 1
            else:
                addresses = list(set([z['formatted_address'] for z in x]))
                if len(addresses) == 1:
                    duration += self.distances.origin_to_lab_times[x[0]['formatted_address']]
                if len(addresses) == 2:
                    duration += self.distances.origin_to_origin_times[(addresses[0], addresses[1])] + min(self.distances.origin_to_lab_times[addresses[0]], self.distances.origin_to_lab_times[addresses[1]])                    
                self.trips_out_counter += 1

        self.modified_durations += duration


        return trips_to_return
