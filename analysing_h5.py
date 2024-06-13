import h5py
import pandas as pd
import numpy
import matplotlib.pyplot as plt


def read_in_h5(filename):
    h5_df = pd.read_hdf(filename)
    h5_df = h5_df.droplevel(0, axis=1)
    return h5_df

def calculate_pupil_diameter(pupil_coordinates):
    # Accessing x and y data for EyeNorth
    eye_north_x = pupil_coordinates['EyeNorth']['x']
    eye_north_y = pupil_coordinates['EyeNorth']['y']
    eye_north_likelihood = pupil_coordinates['EyeNorth']['likelihood']

    # Accessing x and y data for EyeSouth
    eye_south_x = pupil_coordinates['EyeSouth']['x']
    eye_south_y = pupil_coordinates['EyeSouth']['y']
    eye_south_likelihood = pupil_coordinates['EyeSouth']['likelihood']

    # Accessing x and y data for EyeWest
    eye_west_x = pupil_coordinates['EyeWest']['x']
    eye_west_y = pupil_coordinates['EyeWest']['y']
    eye_west_likelihood = pupil_coordinates['EyeWest']['likelihood']

    # Accessing x and y data for EyeEast
    eye_east_x = pupil_coordinates['EyeEast']['x']
    eye_east_y = pupil_coordinates['EyeEast']['y']
    eye_east_likelihood = pupil_coordinates['EyeEast']['likelihood']

    # Calculating pupil diameter and writing it in a list
    diameter_list = []
    for i in range(len(pupil_coordinates.index)):
        d = (numpy.sqrt((eye_north_x[i] - eye_south_x[i]) ** 2 + (eye_north_y[i] - eye_south_y[i]) ** 2) +
             numpy.sqrt((eye_west_x[i] - eye_east_x[i]) ** 2 + (eye_west_y[i] - eye_east_y[i]) ** 2)) / 2
        diameter_list.append(d)

    # Adding the diameter list to the original Dataframe
    pupil_coordinates['EyeTotal', 'Diameter'] = diameter_list
    return pupil_coordinates

def add_timestamps(data_df, frame_rate, total_frames):
    # Adding timestamps to frames based on frame rate of video
    timestamp_sec = []
    timestamp_min = []
    for frames in range(total_frames):
        timestamp_sec.append(frames/frame_rate)
        timestamp_min.append(frames/frame_rate/60)
    data_df['Timestamp', 'Seconds'] = timestamp_sec
    data_df['Timestamp', 'Minutes'] = timestamp_min
    return data_df

# Outlier detection based on "arbitrary" borders and creation of a cleaned DF by excluding outliers
# TO DO:
#   - instead of dropping the data, first determine start and end of actual trials, then interpolate dropped values
#   - add "blink" marker, which identifies when the eyelids are closed to also interpolate these data points
def identify_diameter_outliers(data_df, max_diameter, min_diameter):
    outlier_condition = (data_df['EyeTotal', 'Diameter'] < min_diameter) | (data_df['EyeTotal', 'Diameter'] > max_diameter)
    outlier_values = data_df.loc[outlier_condition, ('EyeTotal', 'Diameter')]
    return outlier_values

# TO-DO: Rethink in which order/steps to identify outliers and then actually drop them because interpolation has to
# happen in-between these steps
def drop_outliers(data_df, outlier_values):
    clean_df = data_df.drop(index=outlier_values.index)
    return clean_df


# Interpolation
# Ideas: Take average of previous 5 points and average of next 5 points and then linear interpolate between those
# Contra: Each tick is 33ms so 5 points already corresponds to 165ms
def drop_start_data(data_df, likelihood_threshold):
    for i in range(len(data_df['LED']['likelihood'])):
        if data_df['LED']['likelihood'][i] > likelihood_threshold:
            data_df.loc[0:i-1].drop()
            return data_df
    print("No start data was dropped")

def interpolate_outliers():
    1==1


def plot_pupil_diameter(data_df):
    # Plotting the Diameter over time
    graph = data_df.plot(x=('Timestamp', 'Minutes'), y=('EyeTotal', 'Diameter'), kind='line')
    plt.show()




