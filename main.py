##"C:\Users\netan\Downloads\DataFeederLog - 0GpsLog.csv"
##r"C:\Users\netan\Downloads\DataFeederLog.xlsx"
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utilities import *
import utm
from scipy.interpolate import interp1d
from plot_tester import Plotter
def main():
    #path_anchors = "0GpsLog.csv"
    # os.makedirs("output_graphs0", exist_ok=True)
    myplot = Plotter()
    myplot.call_all_plts()

if __name__ == "__main__":
    main()
    plt.show()