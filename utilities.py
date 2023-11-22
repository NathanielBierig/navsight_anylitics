import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import utm
from errors import NavSightCrashError

#consider whole thing a class making create file local vars
# gonna change later on when no global var
def parse_all_files():
    gps_data = gpsRead()  # gps'
    kalman_data = KalmanRead() # kalman output
    anchor_data = AnchorsReadFromKalman(kalman_data)
    return gps_data, kalman_data, anchor_data

def syncData(gps_data, kalman_data):
    gps_data_sync = pd.DataFrame(columns=gps_data.columns, index=range(len(kalman_data)))
    f_lat = interp1d(gps_data["navigation-time"].to_numpy().astype(np.float64),
                     gps_data["lat"].to_numpy().astype(np.float64), fill_value="extrapolate")
    f_lon = interp1d(gps_data["navigation-time"].to_numpy().astype(np.float64),
                     gps_data["lon"].to_numpy().astype(np.float64), fill_value="extrapolate")
    f_alt = interp1d(gps_data["navigation-time"].to_numpy().astype(np.float64),
                     gps_data["alt"].to_numpy().astype(np.float64), fill_value="extrapolate")
    gps_data_sync["lat"] = f_lat(kalman_data["Timestamp"].astype(np.float64))
    gps_data_sync["lon"] = f_lon(kalman_data["Timestamp"].astype(np.float64))
    gps_data_sync["alt"] = f_alt(kalman_data["Timestamp"].astype(np.float64))
    gps_data_sync["navigation-time"] = kalman_data["Timestamp"].to_numpy()
    gps_data_sync["AIR_VEHICLE_LOCATION"] = "AIR_VEHICLE_LOCATION"
    return gps_data_sync, kalman_data, gps_data
def error_calc(gps_data_sync, kalman_data, gps_data):
    # first parts just for that kalman alt func
    k_time, k_alt_after = kalman_data["Timestamp"], kalman_data["alt after"]
    gps_alt, gps_navtime = gps_data["alt"].to_numpy().astype(np.float64), gps_data["navigation-time"].to_numpy().astype(np.float64)
    # getting the error rates/ split into own, maybe make own df nvm just access the data from the dds df.
    XY_error = np.sqrt((gps_data_sync["lat"].to_numpy() - kalman_data["lon after"].to_numpy()) ** 2 + (
            gps_data_sync["lon"].to_numpy() - kalman_data["lat after"].to_numpy()) ** 2)
    X_error = gps_data_sync["lat"].to_numpy() - kalman_data["lon after"].to_numpy()
    Y_error = gps_data_sync["lon"].to_numpy() - kalman_data["lat after"].to_numpy()
    Z_error = gps_data_sync["alt"].to_numpy() - kalman_data["alt after"].to_numpy(),
    return XY_error, X_error, Y_error,Z_error, gps_data_sync["navigation-time"].astype(np.float64), k_time, k_alt_after, gps_alt, gps_navtime
# can take z error out as not used anymore nvm its back
# Z_error = gps_data_sync["alt"].to_numpy() - kalman_data["alt after"].to_numpy(), Z_error
def AnchorsReadFromKalman(kalman_data):
    anchors = kalman_data[kalman_data["mes type"] == "ANCHOR_DURING_SLAM"]
    return anchors
def get_a_data(gps_data, anchor_data):
    a_xy_error, _, _, a_z_error, a_nav_timesyncData, _, _, _, _ = error_calc(*syncData(gps_data, anchor_data))
    return a_xy_error, a_z_error, a_nav_timesyncData

def convert_to_utm(lat, lon):
    easting, northing, _, _ = utm.from_latlon(lat, lon)
    return easting, northing

def gpsRead(): #path=path_anchors was in the ()
    #path = r'C:\Users\netan\Downloads\DataFeederLog - DataFeederLog.csv' #0/og
    #path = r'C:\Users\netan\Downloads\1GpsLog - DataFeederLog.csv' #1
    #path = r'C:\Users\netan\Downloads\3GPSLog - DataFeederLog.csv' #3
    path = r'C:\Users\netan\Downloads\gps sabatoge - Sheet1.csv'

    df = pd.read_csv(path)
    if df.shape[0] == 2:
        raise NavSightCrashError(path)
        exit()
    columns_to_select = ['navigation-time', 'AIR_VEHICLE_LOCATION', 'lat', 'lon', 'alt', 'body_orientation[x', 'y', 'z',                    'w]']
    gps_data = df[columns_to_select]
    gps_data = gps_data[gps_data['AIR_VEHICLE_LOCATION'] == 'AIR_VEHICLE_LOCATION']
    gps_data[['UTM Easting', 'UTM Northing']] = gps_data.apply(lambda row: convert_to_utm(row['lat'], row['lon']), axis=1,
                                                               result_type='expand')
    gps_data.drop(['lat', 'lon'], axis=1, inplace=True)
    gps_data.insert(2, 'lat', gps_data.pop('UTM Easting'))
    gps_data.insert(2, 'lon', gps_data.pop('UTM Northing'))
    return gps_data

def KalmanRead():
    #path = r'C:\Users\netan\Downloads\KalmanLog - KalmanLog (2).csv' #0/og
    #path = r'C:\Users\netan\Downloads\1KalmanLog - KalmanLog.csv' #1
    #path = r'C:\Users\netan\Downloads\3KalmanLog - KalmanLog.csv' #3
    path = r'C:\Users\netan\Downloads\kalman sabatoge - Sheet1.csv'

    df = pd.read_csv(path)
    if df.shape[0] == 0:
        raise NavSightCrashError(path)
        exit()
    columns_to_select = ['Timestamp', 'frameId', 'lon after', 'lat after', 'alt after', 'mes type']
    kalman_data = df[columns_to_select]
    return kalman_data





