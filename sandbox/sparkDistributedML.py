from pyspark import SparkContext
from sklearn import svm, datasets
from spark_sklearn import GridSearchCV

# create spark context - use all cores
sc = SparkContext("local[*]", "Simple Test")

# test data
iris = datasets.load_iris()

parameters = {'kernel':('linear', 'rbf'), 'C':[0.01, 0.1, 1, 2, 3, 4, 5, 10]}
svr = svm.SVC()
clf = GridSearchCV(sc, svr, parameters)
clf.fit(iris.data, iris.target)

print(clf.best_estimator_)
print(clf.best_score_)