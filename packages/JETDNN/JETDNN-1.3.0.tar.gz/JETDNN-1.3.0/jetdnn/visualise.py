import tensorflow
from tensorflow import keras
import predict
from keras.utils import plot_model
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re

# get equation

import numpy as np
import tensorflow as tf

def get_equation(model,filename,input_cols,output_col):
    """
    get_equation

    Produce an analytic equation from a trained DNN model, using forward propagation with numerical methods.

    Args:
        model (Tensorflow Model): trained DNN from build_and_test_single.
        input_cols (list): list of input columns as strings (should be the same as those used to test the DNN).

    Returns:
        string: short_eqn, an analytic equation representing the DNN model.
        list: x, the predicted values (should align with those returned by model.predict).
    """

    def activation_relu(input):
        
        for num in input.tolist():
            if num <= 0:
                return 0
        return input
        
    equation = ""

    data = pd.read_csv(filename,sep="\s{3,}|\s{3,}|\t+|\s{3,}\t+|\t+\s{3,}",skipinitialspace=True)

    x = data[input_cols]
    layer_nodes = [len(x),128,128,128,128,1]
    
    for n in range(0,len(model.layers)): # for each layer
        layer = model.layers[n]
        weights = layer.get_weights() # get list of weights for one layer e.g. W[0][1],W[0][2]

        if len(weights) != 2: # if it is a dropout layer, there are no weights, so move to next layer
            print("No weights in this layer")
        else:
            b = weights[1] # define bias
            w = weights[0] # define weights
            nodes = []

            if n != 0:

                for j in range(0,layer_nodes[n]): # for each node (e.g. for each weight in w0 e.g. w01, w02, w03 etc)
                    node = 0
                    node_eqn = ""
                    for i in range(0,len(input_cols)): # for each input, add weights and inputs to node
                        
                        if isinstance(x,pd.DataFrame):
                            col = np.array(x.iloc[:,i]) # gets ith column, converts to numpy array
                        else:
                            col = x[i]
                        
                        node += (col * float(w[i,j])) # gives the jth value in i: ERROR: for some reason w[i,j] has shape 128, should have 3 lists of 128 vals each. Suggest printing weights array for debugging (important). Check get_weights MS Edge folder
                        node_eqn += "x" + str(i) + "*" + str(w[i,j]) + " + "
                    
                    if activation_relu(node + b[j]) is not 0:
                        node += b[j]
                        node_eqn += str(b[j])

                    nodes.append(activation_relu(node)) # add node to node list
                    equation += node_eqn # adds every node to the main equation

                x = nodes # node values become new inputs
    

    # now out of all loops
    
    added_weights = np.zeros(len(input_cols))
    short_eqn = ""

    for i in range(0,len(input_cols)):
        coeff_res = []
        substring = "x" + str(i)
        res = [n for n in range(0,len(equation)) if equation.startswith(substring,n)] # finds positions of xi
        for q in res:
            coeff_res.append(q+3) # gets positions of x-coefficients
        for w in coeff_res:
            added_weights[i] += float(equation[w:w+4]) # sums coefficients of xi

        short_eqn += str(np.round(added_weights[i],3)) + " [" + str(input_cols[i]) + "] " + " + "

    print(str(output_col) + " = " + short_eqn)

    print(equation)

    return short_eqn, equation, np.array(x)


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