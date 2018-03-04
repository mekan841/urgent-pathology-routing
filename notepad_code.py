
import numpy as np
import scipy as sp
import scipy.stats

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0*np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * sp.stats.t._ppf((1+confidence)/2., n-1)
    return m, m-h, m+h

df_with_geocoding = pd.read_csv('/path/to/dataset_one_geocoded_cleaned.csv', sep='\t', header=0)

df = pd.read_csv('/path/to/dataset_one.csv', header=0, index_col=None) 
df[(~df.JobDistance.isnull()) & (df.Fare > 0) & (df.Flagfall < 5)][['MeterOnTime', 'MeterOffTime', 'Fare', 'JobDistance', 'WaitingTime', 'Flagfall', 'TotalFare', 'CarTravellingTime']].to_csv('./file_for_R_input_for_validating_cost_model_on_older_data.csv')

z = []
zz = []
for x in df_with_geocoding.formatted_address:
    if x in origin_to_lab_times:
        z.append(origin_to_lab_times[x])
    else:
        z.append(-1)
    if x in origin_to_lab_distances:
    	zz.append(origin_to_lab_distances[x])
    else:
    	zz.append(-1)

df_with_geocoding['origin_to_lab_times'] = [x/60.0 for x in z]
df_with_geocoding['origin_to_lab_distances'] = [x/1000.0 for x in zz]
df_with_geocoding[['CarTravellingTime','origin_to_lab_times']]

df_with_geocoding[df_with_geocoding.origin_to_lab_times > 0].to_csv('/path/to/dataset_one_geocoded_cleaned_reduced_compare_google_maps_times.csv')
