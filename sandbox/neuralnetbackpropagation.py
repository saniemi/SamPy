"""
Simple script to understand backpropagation in neural nets.
"""
import numpy as np
# set the seed to be deterministic
np.random.seed(1)


def nonlin(x, deriv=False):
    """
    sigmoid function - gives a probability

    :param x: input information
    :param deriv: returns the derivative if True

    :return: a value between 0 and 1 that can be interpreted as probability
    """
    if deriv:
        return x * (1. - x)

    return 1. / (1 + np.exp(-x))


# fake data - 4 observations and 3 features
X = np.array([[0, 0, 1.5],
              [0, 1, 1.5],
              [1, 0, 1.5],
              [1, 1, 1.5]])
# fake labels - no direct correlation to a feature
y = np.array([[0, 1, 1, 0]]).T

# set the number of hidden nodes in each layer
hiddenSize = 8

# modify the gradient descent step size in different layers
alpha1 = 0.8
alpha2 = 0.6

# initialize weights randomly - connects l0 to l1
# have a mean of zero in weight initialization
# first hidden dimensions are 3, hiddenSize for 3 input columns and hS outputs
syn0 = 2*np.random.random((3, hiddenSize)) - 1
# add another hidden layer, dimensions hiddenSize inputs and 1 output
syn1 = 2*np.random.random((hiddenSize, 1)) - 1

# main loop to update the weights based on the errors we make
for tmp in range(100000):
    # forward propagation

    l0 = X # First Layer of the Network, specified by the input data
    l1 = nonlin(np.dot(l0, syn0)) # first  hidden layer
    l2 = nonlin(np.dot(l1, syn1)) # second hidden layer

    # how much did we miss?
    l2_error = y - l2

    if (tmp % 10000) == 0:
        print("Error:" + str(np.mean(np.abs(l2_error))))

    # multiply how much we missed by the
    # slope of the sigmoid at the values in l2
    l2_delta = l2_error * nonlin(l2, deriv=True)

    # how much did each l1 value contribute to the l2 error
    # (according to the weights)
    # this is the backpropagation step
    l1_error = l2_delta.dot(syn1.T)

    # in what direction is the target l1?
    # were we really sure? if so, don't change too much.
    l1_delta = l1_error * nonlin(l1, deriv=True)

    # update weights
    syn1 += alpha2 * l1.T.dot(l2_delta)
    syn0 += alpha1 * l0.T.dot(l1_delta)


print("Weights:")
print(syn0)
print(syn1)
print("Output After Training:")
print(l2)
