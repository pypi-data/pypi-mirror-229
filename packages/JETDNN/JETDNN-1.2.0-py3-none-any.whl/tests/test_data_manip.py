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
g = pkg_resources.get_distribution("jetdnn").version
print("jetdnn version: " + str(g))

# DATA MANIPULATION TESTS

def test_read_data():
    """Tests basic functionality of read_data function to read a .csv or .dat file."""

    testdata = [[10,55,34,65,7],[67,3,45,6,8],[97,35,23,4,90]]
    testdf = pd.DataFrame(testdata,columns=["One","Two","Three","Four","Five"])
    testcsv = testdf.to_csv("filename.csv",index=False,encoding="utf-8")

    output_expected = testdf

    output = jetdnn.predict.read_data(testcsv)
    assert output == output_expected
