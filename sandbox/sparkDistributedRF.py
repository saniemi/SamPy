from pyspark import SparkContext
import numpy as np
from time import time
from operator import itemgetter
from sklearn import grid_search, datasets
from sklearn.ensemble import RandomForestClassifier
from spark_sklearn import GridSearchCV

# Utility function to report best scores
def report(grid_scores, n_top=3):
    top_scores = sorted(grid_scores, key=itemgetter(1), reverse=True)[:n_top]
    for i, score in enumerate(top_scores):
        print("Model with rank: {0}".format(i + 1))
        print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
              score.mean_validation_score,
              np.std(score.cv_validation_scores)))
        print("Parameters: {0}".format(score.parameters))
        print("")

# create spark context - use all cores
sc = SparkContext("local[*]", "Simple Test")

digits = datasets.load_digits()
X, y = digits.data, digits.target

param_grid = {"max_depth": [3, 5, 8, 10, 13, None],
              "max_features": [1, 3, 10, 20],
              "min_samples_split": [1, 3, 10],
              "min_samples_leaf": [1, 3, 10],
              "criterion": ["gini", "entropy"],
              "n_estimators": [500]}
clf = RandomForestClassifier()

#gs = grid_search.GridSearchCV(clf, param_grid=param_grid) # local
gs = GridSearchCV(sc, clf, param_grid=param_grid) # distributed
start = time()
gs.fit(X, y)
print("GridSearchCV took {:.2f} seconds for {:d} candidate settings.".format(time() - start, len(gs.grid_scores_)))
report(gs.grid_scores_)