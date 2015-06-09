__author__ = 'tianzhang'


import sys
import statistics
import math
#To show some messages:
import recsys.algorithm
recsys.algorithm.VERBOSE = True

from recsys.evaluation.prediction import RMSE, MAE
from recsys.datamodel.data import Data

from baseline import Baseline #Import the test class we've just created
import time
start_time = time.time()
#rmsem = []
#for k in range(1, 11):
#    print str(k)+" fold..."
#Dataset
dat_file='ratings_user.csv'

data = Data()
data.load(dat_file, sep=',', format={'col':0, 'row':1, 'value':2})
train, test = data.split_train_test(percent=80)

print train
print test

################ kNN ################
train_item = {}
train_user = {}
for rating, item_id, user_id in train:
    if item_id in train_item:
        train_item[item_id][user_id] = rating
    else:
        train_item[item_id] = {user_id: rating}
    if user_id in train_user:
        train_user[user_id][item_id] = rating
    else:
        train_user[user_id] = {item_id: rating}

# Pearson correlation
def similarity(user1, user2):
    items = list(set(train_user[user1].keys()).intersection(train_user[user2].keys()))
    s1 = 0
    s2 = 0
    s3 = 0
    for item in items:
        item_history = train_item[item].values()
        mean = statistics.mean(item_history)
        s1 += (train_item[item][user1]-mean)*(train_item[item][user2]-mean)
        s2 += math.pow((train_item[item][user1]-mean), 2)
        s3 += math.pow((train_item[item][user2]-mean), 2)
    if math.sqrt(s2*s3) == 0:
        return -sys.float_info.max
    else:
        return s1/(math.sqrt(s2*s3))


# Evaluate
k = 8
rmse = RMSE()
i = 0

for rating, item_id, user_id in test:
    print "==========================================="

    try:
        print i
        i += 1
        dist = {}

        if item_id in train_item.keys():
            for user in train_item[item_id].keys():
                sim = similarity(user_id, user)
                if sim >= 0:
                    if len(dist) < k:
                        dist[user] = sim
                    mindist = min(dist, key=dist.get)
                    if dist[mindist] < sim:
                        del dist[mindist]
                        dist[user] = sim

            ratings = []
            for user in dist.keys():
                ratings.append(train_user[user][item_id])

        print dist
        if len(dist) < 3:
            pred_rating = statistics.mean(train_user[user_id].values())
        else:
            pred_rating = statistics.mean(ratings)
        print pred_rating

        rmse.add(rating, pred_rating)
    except KeyError:
        continue
r = rmse.compute()
#rmsem.append(r)
print "RMSE=%s\n" % r
#print 'RMSE=%s' % statistics.mean(rmsem)
print("Running Time: %s seconds" % (time.time() - start_time))