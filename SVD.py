# -*- coding: utf-8 -*-
"""
Created on Thu May  7 11:35:58 2015

@author: jingyaoqin
"""

import sys

#To show some messages:
import recsys.algorithm
recsys.algorithm.VERBOSE = True

from recsys.algorithm.factorize import SVD
from recsys.datamodel.data import Data
from recsys.evaluation.prediction import RMSE, MAE

#Dataset
PERCENT_TRAIN = 90
dat_file='./Datasets/ml-latest-small/ratings.csv'
data = Data()
data.load(dat_file, sep=',', format={'col':0, 'row':1, 'value':2, 'ids':int})
    # About format parameter:
    #   'row': 1 -> Rows in matrix come from column 1 in ratings.dat file
    #   'col': 0 -> Cols in matrix come from column 0 in ratings.dat file
    #   'value': 2 -> Values (Mij) in matrix come from column 2 in ratings.dat file
    #   'ids': int -> Ids (row and col ids) are integers (not strings)



#Create SVD
list = []
for j in range(0,50,2):
    sum_value = 0.0
    for i in range(1,11):
        #Train & Test data
        train, test = data.split_train_test(percent=PERCENT_TRAIN)

        K=j
        svd = SVD()
        svd.set_data(train)
        svd.compute(k=K, min_values=5, pre_normalize=None, mean_center=True, post_normalize=True)

        #Evaluation using prediction-based metrics
        rmse = RMSE()
        mae = MAE()
        for rating, item_id, user_id in test.get():
            try:
                pred_rating = svd.predict(item_id, user_id)
                rmse.add(rating, pred_rating)
                mae.add(rating, pred_rating)
            except KeyError:
                continue

        print 'RMSE=%s' % rmse.compute()
        sum_value = sum_value + rmse.compute()
    print '-------'
    print 'the k value is %s' %j
    print 'Final RMSE=%s' % sum_value
    print '-------'
    sum_value = sum_value/10
    list.append(sum_value)

print 'i value is'
for i in range(0,51,2):
    print i

print 'list value is'
for i in range(len(list)):
    print list[i]

print 'MAE=%s' % mae.compute()

