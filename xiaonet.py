import random
from itertools import chain

import numpy as np
import matplotlib.pyplot as plt

class Layer:
    """
    Base class for layers in the network.

    Arguments:

        `inbound_layers`: A list of layers with edges into this layer.
    """
    def __init__(self, input_layer=None):
        """ Simple constructor """
        self.input_layer = input_layer
        self.outbound_layers = []
        
        if self.input_layer:
            self.input_layer.outbound_layers.append(self)

    def forward():
        """
        Every layer that uses this class as a base class will
        need to define its own `forward` method.
        """
        raise NotImplementedError

    def backward():
        """
        Every layer that uses this class as a base class will
        need to define its own `backward` method.
        """
        raise NotImplementedError

class Input(Layer):
    """ Represets all the Hidden Layers """
    def __init__(self, weights, bias):
        Layer.__init__(self)
        self.X = None
        self.W = weights
        self.biases = bias

        self.num_neurons = self.W.shape[-1]
        self.num_images = self.W.shape[0]
        self.num_features = self.W.shape[1]

        self.W_gradients = np.empty((self.num_images, self.num_features))
        self.b_gradients = np.empty((self.num_images,))
        self.gradients = np.empty((self.num_images, self.num_features))

        self.value = np.empty((self.num_images, self.num_neurons))

    def _set(self, images):
        self.X = images
        
    def forward(self):
        """Layer: Input.  execute W * X + b for the entire batch"""
        for i in range(self.num_images):
            h = np.dot(self.X[i], self.W[i])
            self.value[i] = h + self.biases[i]

    def backward(self):
        """ Gradient: Input Layer"""
        self.input_gradients = self.outbound_layers[0].gradients
        for i in range(self.num_images):
            self.W_gradients[i] = np.dot(self.W[i], self.input_gradients[i])
            self.b_gradients[i] = np.dot(self.input_gradients[i], self.biases[i])

            self.gradients[i] = self.W_gradients[i] * self.b_gradients[i]

class Hidden(Layer):
        
    def __init__(self, input_layer, weights, bias):
        Layer.__init__(self, input_layer)
        self.X = None
        self.W = weights
        self.biases = bias

        self.num_classes = self.W.shape[-1]
        self.num_images = self.input_layer.num_images

        self.value = np.empty((self.num_images, self.num_classes))
        self.W_gradients = np.empty((self.num_images, self.input_layer.num_neurons))
        self.b_gradients = np.empty((self.num_images,))
        self.gradients = np.empty((self.num_images, self.input_layer.num_neurons))


    def forward(self):
        """ Layer: Hidden.  N * P + b"""
        self.X = self.input_layer.value
        for i in range(self.num_images):
            h = np.dot(self.X[i], self.W[i])
            self.value[i] = h + self.biases[i]
         
    def backward(self):
        """ Gradient: Hidden Layer"""
        self.input_gradients = self.outbound_layers[0].gradients
        for i in range(self.num_images):
            self.W_gradients[i] = np.dot(self.W[i], self.input_gradients[i])
            self.b_gradients[i] = np.dot(self.input_gradients[i], self.biases[i])
            #print(self.W_gradients[i].shape, self.b_gradients[i], (self.W_gradients[i] * self.b_gradients[i]).shape)
            self.gradients[i] = self.W_gradients[i] * self.b_gradients[i]

        # self.input_gradient = self.outbound_layers[0].gradient
        # self.gradient = self.input_gradient * self.w
        # self.gradient1 = self.outbound_layers[0].gradient

# class ReLU(Layer):
        
#     def __init__(self, input_layer):
#         Layer.__init__(self, [input_layer])

#     def forward(self):
#         """ Layer: ReLU.  execute np.maximum"""
#         self.X = self.input_layer.value
#         self.value = np.maximum(self.x, 0)
         
#     def backward(self):
#         raise NotImplementedError

class Softmax(Layer):
    """ Represents a layer that performs the sigmoid activation function. """
    
    def __init__(self, input_layer):
        Layer.__init__(self, input_layer)

        self.num_classes = self.input_layer.num_classes
        self.num_images = self.input_layer.num_images

        self.value = np.empty((self.num_images, self.num_classes))
        self.gradients = np.empty((self.num_images, self.num_classes))

    def _softmax(self, x):
        """
        Calculate Sigmoid

        `x`: A numpy array-like object.
        """
        return np.exp(x) / np.sum(np.exp(x), axis=0)

    def forward(self):
        """ Perform the sigmoid function and set the value. """
        input_value = self.input_layer.value
        for i in range(self.num_images):
            self.value[i] = self._softmax(input_value[i])

    # def _gradient_softmax(self, theta, x, y):
    #     first_calc = _softmax(theta, x) - np.squeeze(y)
    #     final_calc = first_calc.T.dot(x)

    #     input_value = self.input_layer.value

    #     for i in range(self.num_images):
    #         self.gradients[i] = self._gradient_softmax()
    #     return final_calc

    def backward(self):
        """
        Calculates the gradient using the derivative of
        the softmax function.
        """
        for i in range(self.num_images):
            self.gradients[i] = self.value[i].T


class CrossEntropy(Layer):
    def __init__(self, input_layer):
        """
        The multi-class classifier.
        Should be used as the last layer for a network.

        Arguments
            `inbound_layer`: A layer with an activation function.
        """
        # Call the base class' constructor.
        Layer.__init__(self, input_layer)

        self.ideal_output = None
        self.num_classes = self.input_layer.num_classes
        self.num_images = self.input_layer.num_images

        self.tmp_value = np.empty((self.num_images,))

    def forward(self):
        """
        Calculates the cross entropy.
        """
        # Save the computed output for backward.
        self.softmax = self.input_layer.value
        for i in range(self.num_images):
           self.tmp_value[i] = -np.sum(np.multiply(self.ideal_output[i], np.log(self.softmax[i])))

        self.value = np.mean(self.tmp_value)

    def backward(self):
        """
        Calculates the gradient of the cost.
        """
        self.gradient = None

def plot_images(images, labels, pred_labels=None):
    assert len(images) == len(labels) == 4
    
    # Create figure with 2x2 sub-plots.
    fig, axes = plt.subplots(2, 2, figsize=(2,2))
    fig.subplots_adjust(hspace=0.3, wspace=0.3)

    for i, ax in enumerate(axes.flat):
        # Plot image.
        ax.imshow(images[i].reshape((28, 28)), cmap='binary')

        # Show true and predicted classes.
        if pred_labels is None:
            xlabel = "True: {0}".format(labels[i])
        else:
            xlabel = "True: {0}, Pred: {1}".format(cls_true[i], pred_labels[i])

        ax.set_xlabel(xlabel)
        
        # Remove ticks from the plot.
        ax.set_xticks([])
        ax.set_yticks([])


def topological_sort(feed_dict, ideal_output):
    """
    Sort the layers in topological order using Kahn's Algorithm.

    `feed_dict`: A dictionary where the key is a `Input` Layer and the value is the respective value feed to that Layer.
    `ideal_output`: The correct output value for the last activation layer.

    Returns a list of sorted layers.
    """

    input_layers = [n for n in feed_dict.keys()]

    G = {}
    layers = [n for n in input_layers]
    while len(layers) > 0:
        n = layers.pop(0)
        if n not in G:
            G[n] = {'in': set(), 'out': set()}
        for m in n.outbound_layers:
            if m not in G:
                G[m] = {'in': set(), 'out': set()}
            G[n]['out'].add(m)
            G[m]['in'].add(n)
            layers.append(m)

    L = []
    S = set(input_layers)
    while len(S) > 0:
        n = S.pop()

        if isinstance(n, Input):
            n._set(feed_dict[n])
        if isinstance(n, CrossEntropy):
            n.ideal_output = ideal_output
            # there is only 1 input in this example
            n.n_inputs = 1

        L.append(n)
        for m in n.outbound_layers:
            G[n]['out'].remove(m)
            G[m]['in'].remove(n)
            # if no other incoming edges add to S
            if len(G[m]['in']) == 0:
                S.add(m)
    return L


def plot_images(images, labels, cls_pred=None):
    assert len(images) == len(labels) == 4
    
    # Create figure with 2x2 sub-plots.
    fig, axes = plt.subplots(2, 2, figsize=(2,2))
    fig.subplots_adjust(hspace=0.3, wspace=0.3)

    for i, ax in enumerate(axes.flat):
        # Plot image.
        ax.imshow(images[i].reshape((28, 28)), cmap='binary')

        # Show true and predicted classes.
        if cls_pred is None:
            xlabel = "True: {0}".format(labels[i])
        else:
            xlabel = "True: {0}, Pred: {1}".format(cls_true[i], cls_pred[i])

        ax.set_xlabel(xlabel)
        
        # Remove ticks from the plot.
        ax.set_xticks([])
        ax.set_yticks([])


def train_SGD(feed_dict, ideal_output, trainables=[], learning_rate=1e-4):
    """
    Performs many forward passes and a backward passes through
    a list of sorted Layers while performing stochastic gradient
    descent.

    Arguments:

        `feed_dict`: A dictionary where the key is a `Input` Layer and the value is the respective value feed to that Layer.
        `ideal_output`: The correct output value for the last activation layer.
        `trainables`: Inputs that need to be modified by SGD.
        `epochs`: The number of times to train against all training inputs.
        `learning_rate`: The step size for changes by each gradient.
    """

    sorted_layers = topological_sort(feed_dict, ideal_output)
    reversed_layers = sorted_layers[::-1] # see: https://docs.python.org/2.3/whatsnew/section-slices.html
            
    if True:
        # Forward pass
        for n in sorted_layers:
            n.forward()
            
        for n in reversed_layers:
            n.backward()

        # Performs SGD
        layers = sorted_layers[0:-2]
        partials = [item for sublist in [(layer.W_gradients, layer.b_gradients,) for layer in layers] for item in sublist]

        for n in range(len(trainables)):
            if trainables[n].shape == partials[n].shape:
                print("ok")
                trainables[n] -= learning_rate * partials[n]

    return sorted_layers[-1].value
