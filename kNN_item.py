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


#Dataset
dat_file='ratings_item.csv'

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
def similarity(item1, item2):
    users = list(set(train_item[item1].keys()).intersection(train_item[item2].keys()))
    s1 = 0
    s2 = 0
    s3 = 0
    for user in users:
        user_history = train_user[user].values()
        mean = statistics.mean(user_history)
        s1 += (train_item[item1][user]-mean)*(train_item[item2][user]-mean)
        s2 += math.pow((train_item[item1][user]-mean), 2)
        s3 += math.pow((train_item[item2][user]-mean), 2)
    if math.sqrt(s2*s3) == 0:
        return -sys.float_info.max
    else:
        return s1/(math.sqrt(s2*s3))


# Evaluate
rmse = RMSE()

k = 6
i = 0
for rating, item_id, user_id in test:
    print "==========================================="
    #if i == 5:
        #break
    try:
        print i
        i += 1
        if user_id not in train_user.keys():
            pred_rating = statistics.mean(train_user[item_id].values())
        else:
            dist = {}
            for item in train_user[user_id].keys():
                sim = similarity(item_id, item)
                # 3NN
                if len(dist) < k:
                    dist[item] = sim
                mindist = min(dist, key=dist.get)
                if dist[mindist] < sim:
                    del dist[mindist]
                    dist[item] = sim
            print dist
            ratings = []
            for item in dist.keys():
                ratings.append(train_user[user_id][item])

            pred_rating = statistics.mean(ratings)
            if len(dist) < k:
                pred_rating = statistics.mean(train_user[item_id].values())
            else:
                pred_rating = statistics.mean(ratings)

        print pred_rating
        rmse.add(rating, pred_rating)
    except KeyError:
        continue

print 'RMSE=%s' % rmse.compute()
print("Running Time: %s seconds" % (time.time() - start_time))













