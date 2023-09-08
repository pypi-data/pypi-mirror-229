import numpy as np

def softmax(z):
    shiftx = z - np.max(z)
    exps = np.exp(shiftx)
    return exps / np.sum(exps)

def softmax_prime(z):
    labels = z.shape[1]
    der = np.zeros(z.shape)
    for i in range(labels):
        I = np.eye(z.shape[0])
        x = np.reshape(z[:, i], (-1, 1))
        der[:, i:i+1] = np.dot((I - softmax(x).T), softmax(x))
    return der


def sigmoid(z):
    return 1 / (1 + np.exp(-z))

def sigmoid_prime(z):
    return np.multiply(sigmoid(z), (1 - sigmoid(z)))

def dummy_activation(z):
    return z