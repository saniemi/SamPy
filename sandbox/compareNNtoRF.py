"""
Simple example comparing Random Forests to a Neural Network (MLP) in
a binary classification problem.


Dependencies
------------

:requires: matplotlib
:requires: scikit-learn
:requires: keras

Author
------

:author: Sami Niemi (sami.niemi@valtech.co.uk)


Version
-------

:version: 0.1
:date: 1-Apr-2016
"""
import matplotlib.pyplot as plt
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation
from keras.optimizers import SGD, RMSprop
from keras.callbacks import EarlyStopping
import keras.utils.visualize_util


def testNN(X_train, X_test, y_train, y_test, hiddenSize=256, nepochs=1000, dropouts=0.5):
    """
    Train a Neural Network with dropouts and predict test data.

    :param X_train: training data
    :param X_test: test data
    :param y_train: training labels
    :param y_test: test labels
    :param hiddenSize: set the number of hidden nodes in each layer
    :param nepochs: number of times to update the weights
    :param dropouts: dropout fraction - randomly drop units from each layer

    :return: predictions for the test data
    """
    # specify model - input, two middle layers, and output layer
    model = Sequential()
    model.add(Dense(hiddenSize, input_dim=X_train.shape[1], init='uniform', activation='relu'))
    model.add(Dropout(dropouts))
    model.add(Dense(hiddenSize, activation='relu'))
    model.add(Dropout(dropouts))
    model.add(Dense(hiddenSize, activation='relu'))
    model.add(Dropout(dropouts))
    model.add(Dense(1, activation='sigmoid'))

    # set the optimizer and compile
    opt = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
    #opt = RMSprop(lr=0.001, rho=0.9, epsilon=1e-06)
    model.compile(loss='binary_crossentropy', optimizer=opt)

    # fit the model using training data
    model.fit(X_train, y_train, nb_epoch=nepochs, batch_size=2048,
              validation_split=0.1, show_accuracy=True, verbose=1,
              callbacks=[EarlyStopping(monitor='val_loss', patience=10)])
    print('Training completed...')

    # make a figure of the model
    keras.utils.visualize_util.plot(model, to_file='model.png')

    print('predict test data...')
    yhat = model.predict_proba(X_test, batch_size=5000)
    auc = metrics.roc_auc_score(y_test, yhat)
    print('Results:')
    print('NN AUC:', auc)

    return yhat


def createData():
    """
    Create fake binary classification data with 50 features.
    Split the data set to training and testing samples.

    :return: X_train, X_test, y_train, y_test
    """
    X, y = make_classification(n_samples=100000, n_features=50, n_redundant=10, n_informative=20,
                               random_state=1, n_clusters_per_class=30)
    X = StandardScaler().fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)

    return X_train, X_test, y_train, y_test


def testRF(X_train, X_test, y_train, y_test):
    """
    Train a Random Forest classifier and make predictions for test data.

    :param X_train: training data
    :param X_test: test data
    :param y_train: training labels
    :param y_test: test labels

    :return: predictions for the test data
    """
    clf = RandomForestClassifier(n_estimators=1000, max_features=5, n_jobs=-1, verbose=False)
    clf.fit(X_train, y_train)
    yhat = clf.predict_proba(X_test)[:, 1]
    auc = metrics.roc_auc_score(y_test, yhat)
    print('RF AUC:', auc)

    return yhat


def plotAUC(yhatNN, yhatRF, y):
    """
    Plot ROC curve. Compare Neural Net to Random Forests.

    :param yhatNN: Neural Net predictions
    :param yhatRF: Random Forest predictions
    :param y: target labels

    :return: None
    """
    fprNN, tprNN, thresholdsNN = metrics.roc_curve(y, yhatNN)
    fprRF, tprRF, thresholdsRF = metrics.roc_curve(y, yhatRF)

    plt.figure()
    plt.plot(fprNN, tprNN, label='Neural Net')
    plt.plot(fprRF, tprRF, label='Random Forest')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC')
    plt.legend(loc="lower right")
    plt.savefig('ROC.png')
    plt.close()


if __name__ == "__main__":
    X_train, X_test, y_train, y_test = createData()
    yhatNN = testNN(X_train, X_test, y_train, y_test)
    yhatRF = testRF(X_train, X_test, y_train, y_test)
    plotAUC(yhatNN, yhatRF, y_test)
