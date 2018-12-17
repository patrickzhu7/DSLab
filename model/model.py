import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from scipy import stats

xtrain = pd.read_csv("./draftlogs.csv")

n = xtrain.shape[0]

labels = xtrain.Y.values

x, x_test, y, y_test = train_test_split(xtrain,labels,test_size=0.2,train_size=0.8)
x_train, x_cv, y_train, y_cv = train_test_split(x,y,test_size = 0.25,train_size =0.75)

# x_train, y_train = training
# x_cv, y_cv = validation
# x_test, y_test = test
