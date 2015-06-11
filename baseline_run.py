# -*- coding: utf-8 -*-
"""
Created on Thu May  7 13:37:56 2015

@author: jingyaoqin
"""

import sys

#To show some messages:
import recsys.algorithm
recsys.algorithm.VERBOSE = True

from recsys.evaluation.prediction import RMSE, MAE
from recsys.datamodel.data import Data

from baseline import Baseline #Import the test class we've just created

#Dataset
PERCENT_TRAIN = 80
dat_file='./Datasets/ml-latest-small/ratings.csv'
data = Data()
data.load(dat_file, sep=',', format={'col':0, 'row':1, 'value':2, 'ids':int})
#Train & Test data
train, test = data.split_train_test(percent=PERCENT_TRAIN)

baseline = Baseline()
baseline.set_data(train)
baseline.compute() # In this case, it does nothing

# Evaluate
rmse = RMSE()
mae = MAE()
for rating, item_id, user_id in test.get():
    try:
        pred_rating = baseline.predict(item_id, user_id, user_is_row=False)
        rmse.add(rating, pred_rating)
        mae.add(rating, pred_rating)
    except KeyError:
        continue

print 'RMSE=%s' % rmse.compute()
print 'MAE=%s' % mae.compute()