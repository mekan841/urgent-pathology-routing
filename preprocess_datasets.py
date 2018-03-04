
'''
Input:
Mar_to_Jun_combined_pathology_trips.csv             
    the 'raw' spreadsheet which was copied and 
    pasted into one table from the newer format spreadsheets

Output:
Mar_to_Jun_combined_pathology_trips_geocoded.tsv 
    spreadsheet with geocoding results from Google API
    and irrelevant rows removed        

gmaps_geocode_cache.pkl
    cache of google api results for geocoding

''' 

import sys
import os
import re
import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
import googlemaps

GMAPS_GEOCODE_CACHE_PATH = '/path/to/cache_file.pkl'


try:    
    with open(GMAPS_GEOCODE_CACHE_PATH, 'rb') as f:
        GMAPS_GEOCODE_CACHE = pickle.load(f)
except:
    GMAPS_GEOCODE_CACHE = {}

GMAPS = googlemaps.Client(key=KEY_HERE)
 


REPLACEMENTS = [
    # (regex, replacement),
    # (regex, replacement),
    # ...,
    ]


def replacements(s):

    for r, replacement_address in REPLACEMENTS:
        if re.search(r, s):
            return replacement_address

    if '<addressfragment>' not in s and '<addressfragment>' not in s:
        return s + ' <address>'
    return s



def geocode_wrapper(s):
    try:
        geocode_result = GMAPS.geocode(s)
        assert(geocode_result[0])
        return geocode_result
    except:
        print('cannot be geocoded:' + s)
        return None




INPUT_FILE = '/path/to/dataset_one.csv'
# schema: includes: BookingDate,BookingTime,MeterOnDate,MeterOnTime,MeterOffTime,Fare,JobDistance,WaitingTime,Flagfall,TotalFare,PUAddress,DestAddress,DestPlace,CustomerWaitingTime,CarPickupTime,CarAcceptanceTime,CarTravellingTime,Product,KmFromPickup,KmToPickup,DriverName,CarNumber,PUPlace,PUSuburb,DestSuburb

OUTPUT_FILE = '/path/to/dataset_one_geocoded_cleaned.csv'

# load data
df = pd.read_csv(INPUT_FILE, header=0, index_col=0, sep=',')

# Replace origin (Fare From) addresses with addresses that can be parsed by Google. These were found manually 
# The order of the regexes matters

df['Fare From For Geocoding Input'] = df['PUAddress'].apply(replacements)

# a = df.groupby('Fare From For Geocoding Input').agg({"Fare From": lambda x: list(set(x))}).reset_index()
# for i, r in a.iterrows():
#     if len(r['Fare From']) >= 1:
#         print(r['Fare From For Geocoding Input'] + '\t' + ",".join(r['Fare From']))
# sys.exit()

# step 5:
# geocode addresses

input_locations = list(pd.Series.unique(df['Fare From For Geocoding Input']))
latlong = []
c = 0
for s in input_locations:

    geocode_result = None
    if s in GMAPS_GEOCODE_CACHE:
        geocode_result = GMAPS_GEOCODE_CACHE[s]
    else:
        geocode_result = geocode_wrapper(s)
    
    if geocode_result  is not None:
        GMAPS_GEOCODE_CACHE[s] = geocode_result

    if geocode_result is None:
        t = (s, None, None, None)
    else:
        t = (s, geocode_result[0]['formatted_address'], geocode_result[0]['geometry']['location']['lat'], geocode_result[0]['geometry']['location']['lng'], str(geocode_result[0]['types']), json.dumps(geocode_result))
    
    latlong.append(t)

    if c % 10 == 0:
        print(c, len(input_locations))

    c += 1
    

df_latlong = pd.DataFrame(latlong, columns=['input_location', 'formatted_address', 'lat','lng', 'google_types', 'geocode_result'])

df_with_geocoding = pd.merge(df, df_latlong, left_on = 'Fare From For Geocoding Input', right_on = 'input_location', how='left', suffixes=('_x','_y'))
df_with_geocoding.drop('input_location', axis=1, inplace=True)

df_with_geocoding.to_csv(OUTPUT_FILE, sep='\t')


with open(GMAPS_GEOCODE_CACHE_PATH, 'wb') as f:
    pickle.dump(GMAPS_GEOCODE_CACHE, f)


# ----------------------------------------------------------------------------------------------------------------------------------

GMAPS_GEOCODE_CACHE_PATH = './gmaps_geocode_cache.pkl'

try:    
    with open(GMAPS_GEOCODE_CACHE_PATH, 'rb') as f:
        GMAPS_GEOCODE_CACHE = pickle.load(f)
except:
    GMAPS_GEOCODE_CACHE = {}

GMAPS = googlemaps.Client(key=KEY_HERE)

REPLACEMENTS = [
    ## approximately 50 regex replacements for fragmented addresses in dataset
    ]


def replacements(s):

    for r, replacement_address in REPLACEMENTS:
        if re.search(r, s):
            return replacement_address

    if 'hristchurch' not in s and 'angiora' not in s:
        return s + ' Christchurch'
    return s

def geocode_wrapper(s):
    try:
        geocode_result = GMAPS.geocode(s)
        assert(geocode_result[0])
        return geocode_result
    except:
        print('cannot be geocoded:' + s)
        return None

INPUT_FILE = '/path/to/dataset_two.csv'
# schema includes: Trans Date,Trans Time,Trans Day,Fare From,Fare To,Fare excl,GST,Fare incl

OUTPUT_FILE = '/path/to_dataset_two_geocoded_cleaned.tsv'

df = pd.read_csv(INPUT_FILE, header=0, index_col=False, sep=',')

# remove unecessary rows
# Remove fare reversals as they're mostly null records. Not interested in getting a perfect accounting record just parsing the data
df = df[(~df.Narration.str.contains('REVERSAL|reversal'))]
# Remove trips originating at CHL 
df = df[(~df['Fare From'].str.contains('<addresshere>'))]
# Remove trips that do not end at CHL
df = df[df['Fare To'].str.contains('<addresshere>')]

# Replace origin (Fare From) addresses with addresses that can be parsed by Google. These were found manually 
# The order of the regexes matters

df['Fare From For Geocoding Input'] = df['Fare From'].apply(replacements)

# a = df.groupby('Fare From For Geocoding Input').agg({"Fare From": lambda x: list(set(x))}).reset_index()
# for i, r in a.iterrows():
#     if len(r['Fare From']) >= 1:
#         print(r['Fare From For Geocoding Input'] + '\t' + ",".join(r['Fare From']))
# sys.exit()

# geocode addresses

input_locations = list(pd.Series.unique(df['Fare From For Geocoding Input']))
latlong = []
c = 0
for s in input_locations:

    geocode_result = None
    if s in GMAPS_GEOCODE_CACHE:
        geocode_result = GMAPS_GEOCODE_CACHE[s]
    else:
        geocode_result = geocode_wrapper(s)    
    if geocode_result  is not None:
        GMAPS_GEOCODE_CACHE[s] = geocode_result
    if geocode_result is None:
        t = (s, None, None, None)
    else:
        t = (s, geocode_result[0]['formatted_address'], geocode_result[0]['geometry']['location']['lat'], geocode_result[0]['geometry']['location']['lng'], str(geocode_result[0]['types']), json.dumps(geocode_result))
    latlong.append(t)
    if c % 10 == 0:
        print(c, len(input_locations))
    c += 1
    
df_latlong = pd.DataFrame(latlong, columns=['input_location', 'formatted_address', 'lat','lng', 'google_types', 'geocode_result'])
df_with_geocoding = pd.merge(df, df_latlong, left_on = 'Fare From For Geocoding Input', right_on = 'input_location', how='left', suffixes=('_x','_y'))
df_with_geocoding.drop('input_location', axis=1, inplace=True)
df_with_geocoding.to_csv(OUTPUT_FILE, sep='\t')

with open(GMAPS_GEOCODE_CACHE_PATH, 'wb') as f:
    pickle.dump(GMAPS_GEOCODE_CACHE, f)


