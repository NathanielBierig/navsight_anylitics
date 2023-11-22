##"C:\Users\netan\Downloads\DataFeederLog - 0GpsLog.csv"
##r"C:\Users\netan\Downloads\DataFeederLog.xlsx"
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import utm
from scipy.interpolate import interp1d
""""
reconstruct from bottom to top, also consider plt class/func
plots first, get those error vars/parts and use for all, figure out classes, maybe ake them class vars

"""
#no global vars like this
path_anchors = "0GpsLog.csv"

#utilities
def convert_to_utm(lat, lon):
    easting, northing, _, _ = utm.from_latlon(lat, lon)
    return easting, northing


def dataFeeder(path=path_anchors):
    path = '0GpsLog.csv'  #nonglobal vars like this
    df = pd.read_csv(path)
    columns_to_select = ['navigation-time','AIR_VEHICLE_LOCATION','lat','lon','alt','body_orientation[x', 'y', 'z', 'w]']
    datafeeder_data = df[columns_to_select]
    datafeeder_data = datafeeder_data[datafeeder_data['AIR_VEHICLE_LOCATION']=='AIR_VEHICLE_LOCATION']
    datafeeder_data[['UTM Easting', 'UTM Northing']] = datafeeder_data.apply(lambda row: convert_to_utm(row['lat'], row['lon']), axis=1,
                                                       result_type='expand')
    datafeeder_data.drop(['lat', 'lon'], axis=1, inplace=True)
    datafeeder_data.insert(2, 'lat', datafeeder_data.pop('UTM Easting'))
    datafeeder_data.insert(2, 'lon', datafeeder_data.pop('UTM Northing'))
    return datafeeder_data

#parser file/class
def KalmanRead(path=path_anchors):
    path = '0KalmanLog.csv'
    df = pd.read_csv(path)
    columns_to_select = ['Timestamp', 'frameId', 'lon after', 'lat after', 'alt after', 'mes type']
    kalman_data = df[columns_to_select]
    return kalman_data

#utilities
def AnchorsReadFromKalman(kalman_data):
    anchors = kalman_data[kalman_data["mes type"] == "ANCHOR_DURING_SLAM"]

    return anchors

#analytics kinda, first half may be able to be used as
def compareGPSKalman(datafeeder_data, kalman_data, anchors_only = False):
    # Synchronize the datafeeder on the Kalman timestamps
    #assuming variation from photo time to data time is 0
    datafeeder_data_sync = pd.DataFrame(columns=datafeeder_data.columns, index=range(len(kalman_data)))
    f_lat = interp1d(datafeeder_data["navigation-time"].to_numpy().astype(np.float64), datafeeder_data["lat"].to_numpy().astype(np.float64), fill_value="extrapolate")
    f_lon = interp1d(datafeeder_data["navigation-time"].to_numpy().astype(np.float64), datafeeder_data["lon"].to_numpy().astype(np.float64), fill_value="extrapolate")
    f_alt = interp1d(datafeeder_data["navigation-time"].to_numpy().astype(np.float64), datafeeder_data["alt"].to_numpy().astype(np.float64), fill_value="extrapolate")
    datafeeder_data_sync["lat"] = f_lat(kalman_data["Timestamp"].astype(np.float64))
    datafeeder_data_sync["lon"] = f_lon(kalman_data["Timestamp"].astype(np.float64))
    datafeeder_data_sync["alt"] = f_alt(kalman_data["Timestamp"].astype(np.float64))
    datafeeder_data_sync["navigation-time"] = kalman_data["Timestamp"].to_numpy()
    datafeeder_data_sync["AIR_VEHICLE_LOCATION"]="AIR_VEHICLE_LOCATION"
#getting the error rates/ split into own, maybe make own df nvm just access the data from the dds df.
    XY_error = np.sqrt((datafeeder_data_sync["lat"].to_numpy()-kalman_data["lon after"].to_numpy())**2 + (datafeeder_data_sync["lon"].to_numpy()-kalman_data["lat after"].to_numpy())**2)
    X_error = datafeeder_data_sync["lat"].to_numpy()-kalman_data["lon after"].to_numpy()
    Y_error = datafeeder_data_sync["lon"].to_numpy() - kalman_data["lat after"].to_numpy()
    Z_error = datafeeder_data_sync["alt"].to_numpy()-kalman_data["alt after"].to_numpy()
    datafeeder_data_sync["X error"] = X_error
    datafeeder_data_sync["Y error"] = Y_error
    datafeeder_data_sync["XY error"] = XY_error
    datafeeder_data_sync["Z error"] = Z_error
# split off the different parts of this func into new ones in new files,
    #a:anchor/kalman xy error

    fig, ax = plt.subplots(figsize=(25,25))
    ax.plot(datafeeder_data_sync["navigation-time"].astype(float), XY_error)

    ax.set_xlabel("time (s)")
    ax.set_ylabel("XY Error (m)")

    if anchors_only:
        ax.set_title("XY error of anchors")
        fig.savefig("output_graphs0/anchor_xy_error.png")
    else:
        ax.set_title("XY error of KF")
        fig.savefig("output_graphs0/KF_xy_error.png")

    plt.close()
#split long/lat error
    fig, ax = plt.subplots(figsize=(25,25))

    ax.plot(datafeeder_data_sync["navigation-time"].astype(float), X_error, c='r', label="Latitude Error")
    ax.plot(datafeeder_data_sync["navigation-time"].astype(float), Y_error, c='b', label="Longitude Error")
    ax.axhline(np.mean(X_error), linestyle="-", c='r')
    ax.axhline(np.mean(Y_error), linestyle="-", c='b')
    ax.legend()
    ax.set_xlabel("time (s)")
    ax.set_ylabel("XY Error (m)")

    if anchors_only:
        ax.set_title("X and Y error of anchors")
        fig.savefig("output_graphs0/anchor_x_and_y_error.png")
    else:
        ax.set_title("X and Y error of KF")
        fig.savefig("output_graphs0/KF_x_and_y_error.png")
    plt.close()

#split, anchor/k4 accuracy total consieer conbining below
    fig, ax = plt.subplots(figsize=(25,25))
    ax.hist(XY_error, bins=100, density=True, histtype='step', cumulative=True)
    ax.grid(True)
    ax.set_xlabel("XY distance (m)")
    ax.set_ylabel("%")
    if anchors_only:
        ax.set_title("Accuracy of anchors")
        fig.savefig("output_graphs0/Anchor_accuracy.png")
    else:
        ax.set_title("Accuracy of KF")
        fig.savefig("output_graphs0/KF_accuracy.png")
    plt.close()

##potential spit or gtoup with abovesame as above but only x
    fig, ax = plt.subplots(figsize=(25,25))
    ax.hist(X_error, bins=100, density=True, histtype='bar', cumulative=False, label="X")
    ax.grid(True)
    fig.legend()
    ax.set_xlabel("X distance (m)")
    ax.set_ylabel("%")
    plt.xlim(left=-15, right=15)
    if anchors_only:
        ax.set_title("Accuracy of anchors (X axis)")
        fig.savefig("output_graphs0/Anchor_accuracy_x.png")
    else:
        ax.set_title("Accuracy of KF (X axis)")
        fig.savefig("output_graphs0/KF_accuracy_x.png")
    plt.close()

#sa,e as above
    fig, ax = plt.subplots(figsize=(25,25))
    ax.hist(Y_error, bins=100, density=True, histtype='bar', cumulative=False, label="Y")
    ax.grid(True)
    fig.legend()
    ax.set_xlabel("Y distance (m)")
    ax.set_ylabel("%")
    if anchors_only:
        ax.set_title("Accuracy of anchors (Y axis)")
        fig.savefig("output_graphs0/Anchor_accuracy_y.png")
    else:
        ax.set_title("Accuracy of KF (Y axis)")
        fig.savefig("output_graphs0/KF_accuracy_y.png")
    plt.close()

    return datafeeder_data_sync

##reduce clutter in main, should reallly only be func calls, most of this stuff can be.
def main():
    os.makedirs("output_graphs0", exist_ok=True)
    #  in next two, you have a potential prob with the global var, fix to make more robust
    datafeeder_data = dataFeeder()  # gps'
    kalman_data = KalmanRead()  #  kalman output
    anchor_data = AnchorsReadFromKalman(kalman_data)


    #  practitcly asking to be its own func
    # have to change this to something that only gives the datafeeder_data_sync
    anchor_analysis = compareGPSKalman(datafeeder_data, anchor_data, anchors_only=True)
    xy_error = anchor_analysis['XY error'].copy()

    ## PLOTS: shouldnt be in main, make its own thing

    ## ACCURACY OF ANCHORS HISTOGRAM
    fig, ax = plt.subplots(figsize=(25,25))
    ax.hist(xy_error, bins=100, density=True, histtype='step', cumulative=True)
    ax.grid(True)
    ax.set_xlabel("XY distance (m)")
    ax.set_ylabel("%")
    ax.set_title("Accuracy of anchors")
    fig.savefig("output_graphs0/anchor_accuracy_hist.png")
    plt.close()
    #plt.show()

#relative to Kf    ## ALTITUDE OF THE ANCHORS
    fig, ax = plt.subplots(figsize=(25,25))
    ax.plot(anchor_analysis["navigation-time"], anchor_analysis["Z error"])
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Altitude diff GPS/anchors")
    ax.set_title("Anchors altitude")
    fig.savefig("output_graphs0/anchor_altitudes.png")
    plt.close()
    #plt.show()

    ## ALTITUDE OF KALMAN
    fig, ax = plt.subplots(figsize=(25, 25))
    ax.plot(kalman_data["Timestamp"], kalman_data["alt after"], c='b', label="Kalman")
    ax.plot(datafeeder_data["navigation-time"].to_numpy().astype(np.float64), datafeeder_data["alt"].to_numpy().astype(np.float64), c='r', label="GPS")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Altitude (m)")
    ax.set_title("Altitude diff GPS/Kalman out")
    fig.legend()
    fig.savefig("output_graphs0/kalman_altitude.png")
    plt.close()
    #plt.show()


# Display the plot
if __name__ == "__main__":
    main()
    plt.show()