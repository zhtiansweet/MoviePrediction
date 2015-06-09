__author__ = 'tianzhang'
__author__ = 'tianzhang'


import sys
import statistics
import math
#To show some messages:
import recsys.algorithm
recsys.algorithm.VERBOSE = True

from recsys.evaluation.prediction import RMSE, MAE
from recsys.datamodel.data import Data
from operator import itemgetter
import xlsxwriter

from baseline import Baseline #Import the test class we've just created
import time
start_time = time.time()
#Dataset
dat_file='ratings_item.csv'
data = Data()
data.load(dat_file, sep=',', format={'col':0, 'row':1, 'value':2})

workbook = xlsxwriter.Workbook('RMSE_item_1.xlsx')
worksheet = workbook.add_worksheet()
rmse = {}
for p in range(1, 11):
    train, test = data.split_train_test(percent=90)

    #print train
    #print test

    ################ kNN ################
    train_item = {}
    train_user = {}
    sum = 0
    for rating, item_id, user_id in train:
        sum += rating
        if item_id in train_item:
            train_item[item_id][user_id] = rating
        else:
            train_item[item_id] = {user_id: rating}
        if user_id in train_user:
            train_user[user_id][item_id] = rating
        else:
            train_user[user_id] = {item_id: rating}
    average = sum/len(train)
    # Pearson correlation
    def similarity(item1, item2):
        users = list(set(train_item[item1].keys()).intersection(train_item[item2].keys()))
        #print users
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

    print "Computing Similarity Matrix..."
    # Compute distance matrix
    dist = []
    leng = []
    i = 0
    for rating, item_id, user_id in test:
        dist.append([])
        if user_id in train_user.keys() and item_id in train_item.keys():
            for item in train_user[user_id].keys():
                sim = similarity(item_id, item)
                if sim > 0:
                    dist[i].append((item, sim))
        leng.append(len(dist[i]))
        dist[i] = sorted(dist[i], key=itemgetter(1), reverse=True)
        #print str(i)+": "+str(item_id)
        #print dist[i]
        i += 1

    #print dist
    #print "mean leng = "+str(statistics.mean(leng))
    #print "max leng = "+str(max(leng))
    #print "min leng = "+str(min(leng))

    for k in range(3, 61):
        print str(k)+"NN: "+str(p)+" fold..."
        if k not in rmse.keys():
            rmse[k] = []

        result = RMSE()
        i = 0
        for rating, item_id, user_id in test:
            if len(dist[i]) < 10:
                if item_id in train_item.keys():
                    pred_rating = statistics.mean(train_item[item_id].values())
                elif user_id in train_user.keys():
                    pred_rating = statistics.mean(train_user[user_id].values())
                else:
                    pred_rating = average
            else:
                ratings = []
                for j in range(0, k):
                    if j == len(dist[i]):
                        break
                    ratings.append(train_item[dist[i][j][0]][user_id])
                pred_rating = statistics.mean(ratings)
            result.add(rating, pred_rating)
            i += 1
        rmse[k].append(result.compute())
        print "RMSE = "+str(rmse[k][-1])
        worksheet.write(k-2, p, rmse[k][-1])

m = 1
for k in range(3, 61):
    worksheet.write(k-2, 0, k)
    result = statistics.mean(rmse[k])
    worksheet.write(m, 12, result)
    m += 1
    print str(k)+"NN: Average RMSE=%s" % result
workbook.close()