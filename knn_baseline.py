"""
Author: Sofiane Abbar
This is an implementation of TEMP_rel algorithm described in the following articles:

H. Wang, Y.-H. Kuo, D. Kifer, and Z. Li, “A simple baseline for travel
time estimation using large-scale trip data,” in Proceedings of the 24th
ACM SIGSPATIAL International Conference on Advances in Geographic
Information Systems. ACM, 2016, p. 61.

"""

import numpy as np
from sklearn.metrics import mean_absolute_error, median_absolute_error
from sklearn.preprocessing import OneHotEncoder
from datetime import datetime
from sklearn.ensemble import GradientBoostingRegressor
from collections import defaultdict
from random import shuffle
import sys


def mape_score(y_true, y_pred):
	return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def medape_score(y_true, y_pred):
    return np.median(np.abs((y_true - y_pred) / y_true)) * 100

mapes = []
maes = []
nb_trips = []
mean_krws = []
mean_osrms=[]
#
# for hour in range(24):
coordinates = []
hours = []

data = []
kdurs = []
max_duration = 120
min_duration = 3
split = 0.7
city = sys.argv[1]
weekly_speeds = defaultdict(list)
knn_durations = defaultdict(list)
with open('data/%s_zoned.csv' % city) as f:
    f.readline()
    k_dist, k_dur, o_dist, o_dur = [], [], [], []
    for line in f:
        x = line.strip().split(',')
        # discard cases where trips run in zero seconds/minutes
        if float(x[6]) < min_duration or float(x[6]) > 120:
            continue
        kdurs.append(float(x[6]))

        dt = datetime.strptime(x[0], '%m-%d-%y %H:%M')
        hour_of_day = dt.hour
        day_of_week = dt.weekday()


        hours.append(hour_of_day+1)
        k_dur = float(x[6])
        k_dur = int(k_dur)*60 + int((k_dur-int(k_dur))*60)
        o_dist = float(x[7])
        o_dur = float(x[8])
        o_dur = int(o_dur)*60 + int((o_dur-int(o_dur))*60)
        d_zone = x[10]
        s_zone = x[9]
        if d_zone == '-1' or s_zone == '-1':
            continue
        # KNN Baseline
        weekly_speeds[day_of_week*24 + hour_of_day].append(o_dist*1000/k_dur)
        data.append([hour_of_day+1, day_of_week+1, day_of_week*24+hour_of_day, o_dist, o_dur, s_zone, d_zone, k_dur])

hourly_speeds = {k:np.mean(v) for k, v in weekly_speeds.iteritems()}

shuffle(data)
data = data[:300000]

lim = int(len(data)*split)
X = [_[:-1] for _ in data]
Y = [_[-1] for _ in data]


# KNN baseline: for each pair OD, find all durations.
for tu in data[:lim]:
    # -3: source_zone, -2: destination_zone, -1: gt_duration, 2: hour of week.
    knn_durations[(tu[-3], tu[-2])].append((tu[2], tu[-1]))

y_knn = []
knn_pb = 0
for q in X[lim:]:
    tq = 0
    if not knn_durations[(q[-2], q[-1])]:
        y_knn.append(0)
        knn_pb += 1
        continue
    for p_i in knn_durations[(q[-2], q[-1])]:
        tq += p_i[1] * (hourly_speeds[p_i[0]]/hourly_speeds[q[2]])
    y_knn.append(tq/len(knn_durations[(q[-2], q[-1])]))


print 'KNN. Pbs:%s' % knn_pb
print 'MAE:', np.mean(Y[lim:]), mean_absolute_error(Y[lim:], y_knn)
print 'MedAE:', np.median(Y[lim:]), median_absolute_error(Y[lim:], y_knn)
print 'MAPE:', mape_score(np.array(Y[lim:]), np.array(y_knn))
print 'MedAPE:', medape_score(np.array(Y[lim:]), np.array(y_knn))


