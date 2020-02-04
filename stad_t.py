


import numpy as np
from sklearn.metrics import mean_absolute_error, median_absolute_error
from sklearn.preprocessing import OneHotEncoder
from datetime import datetime
from sklearn.ensemble import GradientBoostingRegressor
from collections import defaultdict
from random import shuffle
import sys
from geopy.distance import geodesic

def mape_score(y_true, y_pred):
	return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def medape_score(y_true, y_pred):
    return np.median(np.abs((y_true - y_pred) / y_true)) * 100

mapes = []
maes = []
nb_trips = []
mean_krws = []
mean_osrms=[]
hours = []

data = []
gt_durs = []
max_duration = 120
min_duration = 3
split = 0.7 # training/test split
city = sys.argv[1]
weekly_speeds = defaultdict(list)
knn_durations = defaultdict(list)
src_zone_hour_trips = defaultdict(int)
dst_zone_hour_trips = defaultdict(int)

print 'Reading data'
with open('data/%s_zoned.csv' % city) as f:
    f.readline()
    k_dist, gt_dur, o_dist, o_dur = [], [], [], []
    for line in f:
        x = line.strip().split(',')
        if float(x[6]) < min_duration or float(x[6]) > max_duration:
            continue
        slon, slat, dlon, dlat = map(float, x[1:5])
        gt_durs.append(float(x[6]))
        dt = datetime.strptime(x[0], '%m-%d-%y %H:%M')
        hour_of_day = dt.hour
        day_of_week = dt.weekday()


        hours.append(hour_of_day+1)
        gt_dur = float(x[6])
        gt_dur = int(gt_dur)*60 + int((gt_dur-int(gt_dur))*60)
        o_dist = float(x[7])
        o_dur = float(x[8])
        o_dur = int(o_dur)*60 + int((o_dur-int(o_dur))*60)
        d_zone = x[10]
        s_zone = x[9]
        if d_zone == '-1' or s_zone == '-1':
            continue
        sl = geodesic((slat, slon),(dlat, dlon)).km
        data.append([hour_of_day+1, day_of_week+1, day_of_week*24+hour_of_day, sl, sl/min(1,o_dist), o_dist, o_dur, s_zone, d_zone, gt_dur])
        src_zone_hour_trips[s_zone] += 1
        dst_zone_hour_trips[d_zone] += 1
        # KNN Baseline
        weekly_speeds[day_of_week*24 + hour_of_day].append(o_dist*1000/gt_dur)

hourly_speeds = {k:np.mean(v) for k, v in weekly_speeds.iteritems()}

total_trips = float(sum(src_zone_hour_trips.values()))
print 'adding trip ratios to data'
for _ in data:
    _.insert(-1, 100*src_zone_hour_trips[_[7]]/total_trips)
    _.insert(-1, 100*dst_zone_hour_trips[_[8]]/total_trips)

print 'prepare for training model'
shuffle(data)
data = data[:300000]

# Hot encoder in case you want to convert categorical into numerical
# mask = [isinstance(_, str) for _ in data[0]]
# enc = OneHotEncoder(categorical_features=mask)
# dd = enc.fit_transform(data)
#d ata =  dd.toarray()

lim = int(len(data)*split)
X = [_[:-1] for _ in data]
Y = [_[-1] for _ in data]




#STAD_t: Temporal features
X = [[_[i] for i in [0,1,2,5,6]] for _ in data]
mod = GradientBoostingRegressor(n_estimators=100, max_depth=5)
mod.fit(X[:lim], Y[:lim])
yhat = mod.predict(X[lim:])
print 'STAD_t'
print 'MAE:', np.mean(Y[lim:]), mean_absolute_error(Y[lim:], yhat)
print 'MedAE:', np.median(Y[lim:]), median_absolute_error(Y[lim:], yhat)
print 'MAPE:', mape_score(np.array(Y[lim:]), np.array(yhat))
print 'MedAPE:', medape_score(np.array(Y[lim:]), np.array(yhat))


