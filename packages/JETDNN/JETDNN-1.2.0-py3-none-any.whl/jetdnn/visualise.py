import tensorflow
from tensorflow import keras
import predict
from keras.utils import plot_model
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# get equation

import numpy as np
import tensorflow as tf

def get_equation(model,filename,input_cols):
    """
    get_equation

    Produce an analytic equation from a trained DNN model, using forward propagation with numerical methods.

    Currently assumes each input is a single value, will be changed to accept full input columns.

    Args:
        model (Tensorflow Model): trained DNN from build_and_test_single.
        input_cols (list): list of input columns as strings (should be the same as those used to test the DNN).

    Returns:
        string: short_eqn, an analytic equation representing the DNN model.
        list: x, the predicted values (should align with those returned by model.predict).
    """

    # x is a list of inputs
    # i think W[0] is a list of weights for that layer

    def activation_relu(input):
        if input > 0:
            return input
        else:
            return 0
        
    equation = ""

    data = pd.read_csv(filename)
    x = data[input_cols]
    
    for n in range(len(model.layers)): # for each layer
        layer = model.layers[n]
        weights = layer.get_weights() # get list of weights for one layer e.g. W[0][1],W[0][2]
        b = weights[1] # define bias
        w = weights[0] # define weights
        nodes = []

        if n != 0: # if not the input layer
            for j in range(0,len(w[0])): # for each node (e.g. for each weight in w0 e.g. w01, w02, w03 etc)
                node = 0
                node_eqn = ""
                for i in range(0,len(x)): # for each input, add weights and inputs to node
                    node += float(x[i]@w[i][j])
                    node_eqn += "x" + str(i) + "*" + str(w[i][j]) + " + "
                
                if activation_relu(node + b) != 0:
                    node += b
                    node_eqn += str(b)

                nodes.append(activation_relu(node)) # add node to node list
                equation += node_eqn # adds every node to the main equation

            x = nodes # node values become new inputs
    

    # now out of all loops

    added_weights = np.zeroes(len(input_cols))
    short_eqn = ""

    for i in range(0,len(input_cols)):
        coeff_res = []
        substring = "x" + str(i)
        res = [n for n in range(0,len(equation)) if equation.startswith(substring,n)] # finds positions of xi
        for q in res:
            coeff_res.append(q+3) # gets positions of x-coefficients
        added_weights[i] += equation[coeff_res] # sums coefficients of xi

        short_eqn += str(added_weights[i]) + "x" + str(i) + " + "

    print(short_eqn)

    return short_eqn, x

# VISUALISE MODELS

def display_model(model):

    """
    display_model

    Display a summary and save a Keras plot of a Deep Neural Network model.

    Args:
        model (Tensorflow Model): Deep Neural Network model build with build_and_test_single.
    
    Returns:
        None
    """
    print(model.summary())
    plot_model(model, to_file='dnn_model_plot.png', show_shapes=True, show_layer_names=True)
    return

# density npm plot