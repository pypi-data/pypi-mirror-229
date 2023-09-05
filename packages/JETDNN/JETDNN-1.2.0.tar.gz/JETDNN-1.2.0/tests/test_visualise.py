import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import pytest
import sys
from pathlib import Path

import pkg_resources

main_folder = Path(__file__).parent.parent
sys.path.insert(0, str(main_folder))
sys.path.insert(0, str(main_folder / 'jetdnn'))
sys.path.insert(0, str(main_folder / 'tests'))
os.chdir(main_folder / 'jetdnn')

import jetdnn

"""
Assumes that test_predict is successful.
"""

def test_get_equation():

    filename = "filename.csv"
    input_cols = ["B-field","I_p","triangularity"]
    test_df = pd.read_csv(filename)
    testinput = test_df[input_cols]

    model = jetdnn.predict.build_and_test_single(filename,input_cols,"ped_height")[0]

    output_expected = model.predict(testinput) # uses tensorflow predict function
    output = jetdnn.visualise.get_equation(model,filename,input_cols)[1]

    assert output == pytest.approx(output_expected,abs(1e-3)) # checks that the output of the neural network checks out with the tensorflow predicted values