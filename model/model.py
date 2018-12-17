import pandas as pd
import numpy as np
import xgboost as abg
from sklearn.model_selection import train_test_split, GridSearchCV
from scipy import stats



def results_to_csv(grid, csvname):
	results = pd.DataFrame(grid.cv_results_)
	results.sort_values(by='rank_test_score', inplace=True)
	results.to_csv(csvname, ',')

def tune_model(
	x_data,
	y_data,
	learning_rate=0.1,
	n_estimators=[100, 125, 150],
	max_depth=[5],
	min_child_weight=[1],
	gamma=[0],
	subsample=[0.8],
	colsample_bytree=[0.8],
	seed=[69]
):
	model_params = {
		'learning_rate': learning_rate,
    'n_estimators': n_estimators,
    'max_depth': max_depth,
    'min_child_weight': min_child_weight,
    'gamma': gamma,
    'subsample': subsample,
    'colsample_bytree': colsample_bytree,
    'seed': seed
	}

	xgbc_params = {
    'tree_method': 'gpu_hist',
    'predictor': 'gpu_predictor',
    'updater': 'grow_gpu',
    'n_jobs': -1
	}
	xgb_clf = abg.XGBClassifier(** xgbc_params)

	grid = GridSearchCV(
    xgb_clf,
    model_params,
    cv=5,
    scoring="roc_auc",
    n_jobs=-1,
    verbose=False
	)
	grid.fit(x_data, y_data)

	return grid

	

def main():
	xtrain = pd.read_csv("./draftlogs.csv")
	n = xtrain.shape[0]
	labels = xtrain.Y.values
	x, x_test, y, y_test = train_test_split(xtrain,labels,test_size=0.2,train_size=0.8)
	x_train, x_cv, y_train, y_cv = train_test_split(x,y,test_size = 0.25,train_size =0.75)

	grid_result = tune_model(x_data=xtrain, y_data=labels)
	results_to_csv(grid_result, "init_train.csv")

if __name__ == "__main__":
	main()
