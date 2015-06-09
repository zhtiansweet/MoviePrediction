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
#import time
#start_time = time.time()
#Dataset
dat_file='ratings_user.csv'
data = Data()
data.load(dat_file, sep=',', format={'col':0, 'row':1, 'value':2})

workbook = xlsxwriter.Workbook('RMSE_user.xlsx')
worksheet = workbook.add_worksheet()
rmse = {}
for p in range(1, 11):
    train, test = data.split_train_test(percent=90)
    try:
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

        print "Computing Similarity Matrix..."
        # Compute distance matrix
        dist = []
        leng = []
        i = 0
        for rating, item_id, user_id in test:
            dist.append([])
            if item_id in train_item.keys() and user_id in train_user.keys():
                for user in train_item[item_id].keys():
                    sim = similarity(user_id, user)
                    if sim > 0:
                        dist[i].append((user, sim))
            leng.append(len(dist[i]))
            dist[i] = sorted(dist[i], key=itemgetter(1), reverse=True)
            #print dist[i]
            i += 1

        #print dist
        #print "mean leng = "+str(statistics.mean(leng))
        #print "max leng = "+str(max(leng))
        #print "min leng = "+str(min(leng))

        for k in range(3, 16):

            print str(k)+"NN: "+str(p)+" fold..."
            if k not in rmse.keys():
                rmse[k] = []

            result = RMSE()
            i = 0
            for rating, item_id, user_id in test:
                if len(dist[i]) < 3:
                    if user_id in train_user.keys():
                        pred_rating = statistics.mean(train_user[user_id].values())
                    elif item_id in train_item.keys():
                        pred_rating = statistics.mean(train_item[item_id].values())
                    else:
                        pred_rating = average
                else:
                    ratings = []
                    for j in range(0, k):
                        if j == len(dist[i]):
                            break
                        ratings.append(train_user[dist[i][j][0]][item_id])
                    pred_rating = statistics.mean(ratings)
                result.add(rating, pred_rating)
                i += 1
            rmse[k].append(result.compute())
            print "RMSE = "+str(rmse[k][-1])
            worksheet.write(k-2, p, rmse[k][-1])
    except KeyError:
        continue


# Create an new Excel file and add a worksheet.

m = 1
for k in range(3, 16):
    worksheet.write(k-2, 0, k)
    result = statistics.mean(rmse[k])
    worksheet.write(m, 12, result)
    m += 1
    print str(k)+"NN: Average RMSE=%s" % result
workbook.close()
