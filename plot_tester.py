# make the class and have clas vars of the errors, each plot func will now be a method
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
from utilities import syncData, parse_all_files, get_a_data, error_calc
import os
#for usin the anchor analisis, make it turn on some class boolean var that flips all the switches,
#orr just all new funcs, would be easier but not as clean
class Plotter:
    def __init__(self):
        self.l_xy_error, self.l_x_error, self.l_y_error, _, self.l_nav_time, self.l_k_time, self.l_k_alt_after, self.l_gps_alt, self.l_gps_nav_time = error_calc(*syncData(*parse_all_files()[:2]))
        self.l_a_xy_error, self.l_a_z_error, self.l_a_nav_time = get_a_data(parse_all_files()[0], parse_all_files()[2])
        self.l_trial_num = 4 # to diferentiate between different flight's data(for save file)
        #eventual goal of above will be utilized well if every file is saved the same e.g. KalmanLog.csv,
        # after the first they will start being KalmanLog.csv(1) ... if given large data will be helpful
        #can use \(\d+\) (not tested thoughroghly) to get val
        # other idea is to do have user enter number and that chooses which flight(would set this var and you jus f{} to path)
        # or just add all paths to list if theyre different and chose like that or dictioanary, (ca use id/dates than)
        #example: input(which flight do you want to see?) -> either f string into path or take it from a dict/list of paths -> run program
        # example windows csv (can proprably use docker container to change for linux/mac)"C:\Users\netan\Downloads\teste - Sheet1 (1).csv"


    def call_all_plts(self):

        os.makedirs(f"output_graphs{self.l_trial_num}", exist_ok=True)
        methods = dir(self)
        for method in methods:
            if not (method.startswith('__') or method == 'call_all_plts'or method.startswith('l_')):
                getattr(self, method)()
                #if not (method == 'anchor_acc_hist' or method == 'anchor_alt_acc' or method == 'kalman_alt_acc'):
                if method not in ['anchor_acc_hist', 'anchor_alt_acc', 'kalman_alt_acc']:
                    getattr(self, method)(anchors_only= True)

    def a_KF_XY_error(self, anchors_only=False):
        fig, ax = plt.subplots(figsize=(25, 25))
        ax.plot(self.l_nav_time, self.l_xy_error)
        ax.set_xlabel("time (s)")
        ax.set_ylabel("XY Error (m)")

        # it's marked out as false so commentig out atm
        if anchors_only:
            ax.set_title("XY error of anchors")
            fig.savefig(f"output_graphs{self.l_trial_num}/anchor_xy_error.png")
        else:
            ax.set_title("XY error of KF")
            fig.savefig(f"output_graphs{self.l_trial_num}/KF_xy_error.png")
        plt.close()

    def a_KF_ll_error(self, anchors_only=False):
        fig, ax = plt.subplots(figsize=(25, 25))

        ax.plot(self.l_nav_time, self.l_x_error, c='r', label="Latitude Error")
        ax.plot(self.l_nav_time, self.l_y_error, c='b', label="Longitude Error")
        ax.axhline(np.mean(self.l_x_error), linestyle="-", c='r')
        ax.axhline(np.mean(self.l_y_error), linestyle="-", c='b')
        ax.legend()
        ax.set_xlabel("time (s)")
        ax.set_ylabel("XY Error (m)")

        if anchors_only:
            ax.set_title("X and Y error of anchors")
            fig.savefig(f"output_graphs{self.l_trial_num}/anchor_x_and_y_error.png")
        else:
            ax.set_title("X and Y error of KF")
            fig.savefig(f"output_graphs{self.l_trial_num}/KF_x_and_y_error.png")
        plt.close()

    def a_kf_accuracy(self, anchors_only=False):
        fig, ax = plt.subplots(figsize=(25, 25))
        ax.hist(self.l_xy_error, bins=100, density=True, histtype='step', cumulative=True)
        ax.grid(True)
        ax.set_xlabel("XY distance (m)")
        ax.set_ylabel("%")
        if anchors_only:
            ax.set_title("Accuracy of anchors")
            fig.savefig(f"output_graphs{self.l_trial_num}/Anchor_accuracy.png")
        else:
            ax.set_title("Accuracy of KF")
            fig.savefig(f"output_graphs{self.l_trial_num}/KF_accuracy.png")
        plt.close()

    def x_a_kf_accuracy(self, anchors_only=False):
        fig, ax = plt.subplots(figsize=(25, 25))
        ax.hist(self.l_x_error, bins=100, density=True, histtype='bar', cumulative=False, label="X")
        ax.grid(True)
        fig.legend()
        ax.set_xlabel("X distance (m)")
        ax.set_ylabel("%")
        plt.xlim(left=-15, right=15)
        if anchors_only:
            ax.set_title("Accuracy of anchors (X axis)")
            fig.savefig(f"output_graphs{self.l_trial_num}/Anchor_accuracy_x.png")
        else:
            ax.set_title("Accuracy of KF (X axis)")
            fig.savefig(f"output_graphs{self.l_trial_num}/KF_accuracy_x.png")
        plt.close()

    def y_a_kf_accuracy(self, anchors_only=False):
        fig, ax = plt.subplots(figsize=(25, 25))
        ax.hist(self.l_y_error, bins=100, density=True, histtype='bar', cumulative=False, label="Y")
        ax.grid(True)
        fig.legend()
        ax.set_xlabel("Y distance (m)")
        ax.set_ylabel("%")
        if anchors_only:
            ax.set_title("Accuracy of anchors (Y axis)")
            fig.savefig(f"output_graphs{self.l_trial_num}/Anchor_accuracy_y.png")
        else:
            ax.set_title("Accuracy of KF (Y axis)")
            fig.savefig(f"output_graphs{self.l_trial_num}/KF_accuracy_y.png")
        plt.close()

    def anchor_acc_hist(self):

        fig, ax = plt.subplots(figsize=(25, 25))
        ax.hist(self.l_a_xy_error, bins=100, density=True, histtype='step', cumulative=True)
        ax.grid(True)
        ax.set_xlabel("XY distance (m)")
        ax.set_ylabel("%")
        ax.set_title("Accuracy of anchors")
        fig.savefig(f"output_graphs{self.l_trial_num}/anchor_accuracy_hist.png")
        plt.close()

    def anchor_alt_acc(self):
        fig, ax = plt.subplots(figsize=(25, 25))
        #No idea why i had to reshape this one(and only), was coming out as (1,202) instead of 202,
        ax.plot(self.l_a_nav_time, np.array(self.l_a_z_error).reshape(len(self.l_a_nav_time,)))
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Altitude diff GPS/anchors")
        ax.set_title("Anchors altitude")
        fig.savefig(f"output_graphs{self.l_trial_num}/anchor_altitudes.png")
        plt.close()

    #dont see worth in creating local vars as will only be used once
    #nvm will make easier to call all
    def kalman_alt_acc(self):
        fig, ax = plt.subplots(figsize=(25, 25))
        ax.plot(self.l_k_time, self.l_k_alt_after, c='b', label="Kalman")
        ax.plot(self.l_gps_nav_time, self.l_gps_alt, c='r', label="GPS")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Altitude (m)")
        ax.set_title("Altitude diff GPS/Kalman out")
        fig.legend()
        fig.savefig(f"output_graphs{self.l_trial_num}/kalman_altitude.png")
        plt.close()
