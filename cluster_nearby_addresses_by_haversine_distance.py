import sys
import os
import re
import json
import numpy as np
import pandas as pd
from datetime import datetime
import googlemaps
import itertools
import math
from collections import defaultdict

import matplotlib.pyplot as plt
import time
from sklearn.cluster import DBSCAN
from sklearn import metrics
import copy
import itertools

# -----------------------------------------------------------------------------
# Load Data
# -----------------------------------------------------------------------------

INPUT_FILE = ''

df = pd.read_csv(INPUT_FILE, header=0, index_col=0, sep='\t')
dfraw = df.copy()

# -----------------------------------------------------------------------------
# Calculate Trips Per Day
# -----------------------------------------------------------------------------

df = dfraw.copy()
df['Trans DateDT'] = pd.to_datetime(df['Trans Date'], format='%d/%m/%Y')
df = df.set_index('Trans DateDT')
#df = df[df.index >= '2017-03-10'].copy()

df['cnt'] = 1

#df.index = df['Trans DateDT']
daily_series = df['cnt'].resample('D').sum()
grouper = df.groupby([pd.TimeGrouper('1D'), 'formatted_address'])
# grouper = df.groupby([pd.TimeGrouper('1D'), 'Fare From'])
grouper['cnt'].sum()
origin_trips_by_day = pd.DataFrame(grouper['cnt'].sum()).reset_index()
origin_trips_by_day.pivot(index='Trans DateDT', columns='formatted_address', values='cnt')
origin_trips_by_day.pivot(index='Trans DateDT', columns='formatted_address', values='cnt').to_csv('/path/to/origin_trip_counts_by_day_pivoted.csv')
# origin_trips_by_day.pivot(index='Trans DateDT', columns='Fare From', values='cnt')
# origin_trips_by_day.pivot(index='Trans DateDT', columns='Fare From', values='cnt').to_csv('./origin_trip_counts_by_day_pivoted.csv')


# find average trips per day
a = df.groupby('formatted_address').agg({"cnt":sum}).sort_values(by='cnt', ascending=False)
a['cnt'] / pd.Series.nunique(origin_trips_by_day['Trans DateDT'])




# -----------------------------------------------------------------------------
# Calculate Trips Per Hour daily time series
# -----------------------------------------------------------------------------

df = dfraw.copy()
df['Trans DateDT'] = pd.to_datetime(df['Trans Date'] + " " + df['Trans Time'], format='%d/%m/%Y %H:%M:%S')
df = df.set_index('Trans DateDT')
#df = df[df.index >= '2017-03-10'].copy()

# df = df[df.formatted_address.str.contains('401')]

df['cnt'] = 1

#df.index = df['Trans DateDT']
daily_series = df['cnt'].resample('H').sum()
grouper = df.groupby([pd.TimeGrouper('1H'), 'formatted_address'])
# grouper = df.groupby([pd.TimeGrouper('1D'), 'Fare From'])
grouper['cnt'].sum()
origin_trips_by_hour = pd.DataFrame(grouper['cnt'].sum()).reset_index()
origin_trips_by_hour['thehour'] = [x.hour for x in origin_trips_by_hour['Trans DateDT']]

origin_trips_by_hour_grouped = origin_trips_by_hour.groupby(['formatted_address','thehour']).agg({"cnt": sum}).reset_index()
origin_trips_by_hour_grouped['cnt_new'] = origin_trips_by_hour_grouped.cnt/origin_trips_by_hour_grouped.groupby('formatted_address').cnt.transform('sum')

origin_trips_by_hour_grouped.groupby('thehour').agg({"cnt":sum}).reset_index().plot(x='thehour', y='cnt')
plt.show()


# -----------------------------------------------------------------------------
# Find NZMG coordinates for origin locations
# -----------------------------------------------------------------------------


def dd2dms(deg):
    # decimal degrese to degrees minutes seconds
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = (md - m) * 60
    return (d, m, sd)


INPUT_FILE = '/path/to/dataset_two_geocoded_cleaned.tsv'
df = pd.read_csv(INPUT_FILE, header=0, index_col=0, sep='\t')

df_grouped_by_fa = df.groupby(['formatted_address']).agg({"lat":[np.min, np.mean, np.max, pd.Series.nunique, lambda x: list(set(x))], "lng":[np.min, np.mean, np.max, pd.Series.nunique, lambda x: list(set(x))], "Fare incl": len, "Fare From For Geocoding Input": 
lambda x: list(set(x)), "Fare From": lambda x: list(set(x)), "google_types": lambda x: list(set(x))}).reset_index().sort_values(by='formatted_address', ascending=False)
df_grouped_by_fa.columns = ['_'.join(col).strip() for col in df_grouped_by_fa.columns.values]
df_grouped_by_fa.rename(columns={'Fare incl_len': 'trip_count'}, inplace=True)
df_grouped_by_fa['trip_count'] = df_grouped_by_fa['trip_count'].astype(int)

for i, r in df_grouped_by_fa.iterrows():
    formatted_address = r['formatted_address_']
    lat = r['lat_mean']
    lng = r['lng_mean']
    latdd = dd2dms(lat)
    lngdd = dd2dms(lng)
    lat_str = " ".join([str(x) for x in latdd]) + " S"
    lng_str = " ".join([str(x) for x in lngdd]) + " E"
    s = lat_str + " " + lng_str
    print(formatted_address + '\t' + str(lat) + '\t' + str(lng) + '\t' + str(s))
    # print(s)

## at this point, copy these coordinates into the LINZ API at 
# http://apps.linz.govt.nz/coordinate-conversion/index.aspx?do_entry=1&ADVANCED=1&NEXT=&IS=WGS84_G1762&IO=NE&IC=H&IH=-&ID=&PN=N&IF=F&OS=NZMG&OO=NE&OC=H&OH=-&OP=&OF=H&OD=&CI=Y&YEAR=now&MODE=&VSN=2
# http://apps.linz.govt.nz/coordinate-conversion/index.aspx?Advanced=1&IS=WGS84&OS=NZMG&IO=NE&IC=H&IH=-&OO=NE&OC=H&OH=-&PN=N&IF=T&ID=%20&OF=H&OD=%20&CI=Y&do_entry=Enter%20coordinates&DEBUG=&ADVANCED=0
## then create ./fomatted_address_NZMG_from_mean_WGS84_coords_and_LINZ_website.csv

nzmg = pd.read_csv('/path/to/fomatted_address_NZMG_from_mean_WGS84_coords_and_LINZ_website.csv', header=0, index_col=False)
nzmg = nzmg.reset_index()
nzmg.rename(columns={'index': 'location_id'}, inplace=True)
# nzmg.to_csv('/home/alanw/data/chl/fomatted_address_NZMG_from_mean_WGS84_coords_and_LINZ_website_with_id.csv', index=False)


fig, ax = plt.subplots()
ax.margins(0.05) # Optional, just adds 5% padding to the autoscaling
ax.plot(nzmg.Easting, nzmg.Northing, marker='o', linestyle='', ms=5)
ax.legend()
plt.show()


# -----------------------------------------------------------------------------
# For every origin, find origins 
# -----------------------------------------------------------------------------



nzmg = pd.read_csv('/path/to/fomatted_address_NZMG_from_mean_WGS84_coords_and_LINZ_website_with_id.csv', header=0, index_col=False)

GMAPS = googlemaps.Client(key=KEYHERE)

def mygrouper(n, iterable):
    args = [iter(iterable)] * n
    return ([e for e in t if e != None] for t in itertools.zip_longest(*args))

z = list(zip(nzmg.decimal_lat, nzmg.decimal_lng, nzmg.location_id))
z_grouped = list(mygrouper(10,z)) 

c = 0
output = []
for zi in z_grouped:
    for zj in z_grouped:
        dm = GMAPS.distance_matrix([(i[0],i[1]) for i in zi], [(i[0],i[1]) for i in zj], mode='driving', units='metric', departure_time=1504134000, traffic_model='best_guess')
        output.append(([i[2] for i in zi], [i[2] for i in zj], dm))
    print(c)
    c += 1

# dm_duration_in_traffic = np.zeros((len(nzmg),len(nzmg)))
# dm_distance = np.zeros((len(nzmg),len(nzmg)))
# dm_duration = np.zeros((len(nzmg),len(nzmg)))
nzmg_dm_df = []
for t in output:
    origin_address_ids = t[0]
    destination_address_ids = t[1]
    js = t[2]

    for i in range(len(origin_address_ids)):
        for j in range(len(destination_address_ids)):
            # dm_duration_in_traffic[origin_address_ids[i], destination_address_ids[j]] = js['rows'][i]['elements'][j]['duration_in_traffic']['value']
            # dm_duration[origin_address_ids[i], destination_address_ids[j]] = js['rows'][i]['elements'][j]['duration']['value']
            # dm_distance[origin_address_ids[i], destination_address_ids[j]] = js['rows'][i]['elements'][j]['distance']['value']
            try:
                nzmg_dm_df.append((nzmg.iloc[origin_address_ids[i]].location_id, nzmg.iloc[destination_address_ids[j]].location_id, nzmg.iloc[origin_address_ids[i]].formatted_address, nzmg.iloc[destination_address_ids[j]].formatted_address, js['rows'][i]['elements'][j]['duration_in_traffic']['value'], js['rows'][i]['elements'][j]['duration']['value'], js['rows'][i]['elements'][j]['distance']['value']))
            except:
                nzmg_dm_df.append((nzmg.iloc[origin_address_ids[i]].location_id, nzmg.iloc[destination_address_ids[j]].location_id, nzmg.iloc[origin_address_ids[i]].formatted_address, nzmg.iloc[destination_address_ids[j]].formatted_address, js['rows'][i]['elements'][j]['duration']['value'], js['rows'][i]['elements'][j]['duration']['value'], js['rows'][i]['elements'][j]['distance']['value']))

nzmg_dm_df = pd.DataFrame(nzmg_dm_df, columns = ['origin_location_id','destination_location_id', 'origin_address','destination_address','duration_in_traffic', 'duration', 'distance'])
nzmg_dm_df.to_csv('/path/to/fomatted_address_NZMG_from_mean_WGS84_coords_and_LINZ_website_with_id_distance_matrix.csv', index=False)

# -----------------------------------------------------------------------------
# Find relationship between travel time and Fare excl cost
# -----------------------------------------------------------------------------

def get_cost_for_travel_duration(t):
    if t > 599 and t < 601:
        return 9.95
    if t > 1079 and t < 1081:
        return 9.95*2
    return 0.031088293631141 * t - 5.58

duration_in_traffic_to_fare = []
 
for i, r in df.iterrows():

    origin = r['formatted_address']
    fare = r['Fare excl']

    duration_in_traffic = origin_to_lab_times[origin]
    duration_in_traffic_to_fare.append(duration_in_traffic)

df['duration_in_traffic'] = duration_in_traffic_to_fare
df[['duration_in_traffic', 'Fare excl']].to_csv('/path/to/duration_in_traffic_to_fare.csv')
