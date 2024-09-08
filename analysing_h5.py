import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy

from math import factorial


def read_in_h5(filename):
    h5_df = pd.read_hdf(filename)
    h5_df = h5_df.droplevel(0, axis=1)
    return h5_df


# This one is heavily reliant on the structure staying the same - definitely something to look out for before deciding
# on the final workflow for running all the analysis
def read_in_behav(filename):
    behav_data = pd.read_csv(filename, header=None, names=['Direction', 'Correct', 'ReactionTimeLeft',
                                                           'ReactionTimeRight', 'StartTime'])
    behav_data['Correct'] = behav_data['Correct'].astype(int)
    return behav_data


def code_lick_direction(data):
    data['Decision'] = 0
    for i in range(len(data)):
        if np.isnan(data['ReactionTimeLeft'][i]) and np.isnan(data['ReactionTimeRight'][i]):
            data.loc[i, 'Decision'] = 0
        if not np.isnan(data['ReactionTimeLeft'][i]) and np.isnan(data['ReactionTimeRight'][i]):
            data.loc[i, 'Decision'] = 1
        if np.isnan(data['ReactionTimeLeft'][i]) and not np.isnan(data['ReactionTimeRight'][i]):
            data.loc[i, 'Decision'] = 2
    return data


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
        d = (np.sqrt((eye_north_x[i] - eye_south_x[i]) ** 2 + (eye_north_y[i] - eye_south_y[i]) ** 2) +
             np.sqrt((eye_west_x[i] - eye_east_x[i]) ** 2 + (eye_west_y[i] - eye_east_y[i]) ** 2)) / 2
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


def drop_unimportant_columns(data_df, unimportant_columns):
    for column in unimportant_columns:
        data_df = data_df.drop(column, axis=1, level=0)
    return data_df


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
    1 == 1


def plot_pupil_diameter(data_df, ax):
    # Plotting the Diameter over time
    data_df.plot(x=('Timestamp', 'Minutes'),
                 y=('EyeTotal', 'Diameter'),
                 kind='line',
                 ax=ax,
                 label='unsmooth')

def smoothing_savitzky_golay(x, window_size, order, deriv=0):
    final_signal = scipy.signal.savgol_filter(x,window_size,order,deriv)
    return final_signal


def plot_smooth_graph(data_df, signal_arr, ax):
    diameter_plot_smooth = pd.DataFrame({'Timestamp': data_df['Timestamp']['Minutes'],
                                         'Diameter': signal_arr})
    smooth_graph = diameter_plot_smooth.plot(x='Timestamp',
                          y='Diameter',
                          kind='line',
                          ax=ax,
                          label='smooth',
                          color='red')


def merge_smoothed_data(data_df, smoothed_signal):
    data_df.loc[:, ('EyeTotal', 'Diameter')] = smoothed_signal
    return data_df


def break_into_trials(df):
    # Initialize an empty list to store trial data
    trial_data = []
    trial_count = 1

    # Iterate through the dataframe row by row (starting from the second row to compare with the previous row)
    for i in range(1, len(df)):
        # Get current and previous likelihood values using iloc (position-based)
        current_likelihood = df.iloc[i][('LED', 'likelihood')]
        previous_likelihood = df.iloc[i - 1][('LED', 'likelihood')]

        # Condition 1: If current likelihood > 0.9 and previous likelihood <= 0.9 (Start condition)
        if current_likelihood > 0.9 and previous_likelihood <= 0.9:
            # Store the start of a trial
            start_time = df.iloc[i][('Timestamp', 'Minutes')]

        # Condition 2: If current likelihood <= 0.9 and previous likelihood > 0.9 (End condition)
        elif current_likelihood <= 0.9 and previous_likelihood > 0.9:
            # Store the end of the trial and append the trial data to the list
            end_time = df.iloc[i - 1][('Timestamp', 'Minutes')]
            trial_data.append({'Trial': trial_count, 'Start': start_time, 'End': end_time})
            trial_count += 1  # Move to the next trial

    # Convert the trial_data list to a DataFrame
    trial_df = pd.DataFrame(trial_data)

    return trial_df

# Start Time in Trial_DF is saved in minutes, so 3s are subtracted from the minutes to get the baseline
# as there won't be always an exactly perfectly matching timestamp, the one closes to the calculated timestamp
# will be chosen
def estimate_baseline(data_df, trial_df):
    i = 0
    for minutes in trial_df['Start']:
        baseline_timestamp = minutes - (3 / 60)
        closest_timestamp = (data_df['Timestamp']['Minutes'] - baseline_timestamp).abs().idxmin()
        baseline_diameter = data_df.loc[closest_timestamp, ('EyeTotal', 'Diameter')]
        trial_df.loc[i, 'Baseline'] = baseline_diameter
        i += 1
    return trial_df


def add_performance_data(pupil_df, behav_data):
    i = 0
    # not happy with that but to prevent the df interpreting the values as float the column needs to be created first
    # that's why it's only for "Direction" and "Correct" as these need to be int. The other times need to be float.
    pupil_df['Direction'] = 0
    pupil_df['Decision'] = 0
    pupil_df['Correct'] = 0
    for trial in pupil_df['Trial']:
        pupil_df.loc[i, 'Direction'] = behav_data.loc[i, 'Direction']
        pupil_df.loc[i, 'Decision'] = behav_data.loc[i, 'Decision']
        pupil_df.loc[i, 'Correct'] = behav_data.loc[i, 'Correct']
        pupil_df.loc[i, 'ReactionTimeLeft'] = behav_data.loc[i, 'ReactionTimeLeft']
        pupil_df.loc[i, 'ReactionTimeRight'] = behav_data.loc[i, 'ReactionTimeRight']
        i += 1
    return pupil_df


def plot_performance_graph(trial_df, data_df, ax):
    # Example data for the line plot
    x = data_df['Timestamp']['Minutes']
    y = data_df['EyeTotal']['Diameter']

    # Plot the line
    plt.plot(x, y, label='Pupil Diameter', color=(0.5,0.5,0.5))

    x_base = trial_df['End']
    y_base = trial_df['Baseline']
    moving_average = trial_df['Baseline'].rolling(window=4).mean()
    plt.plot(x_base, moving_average, label='Baseline Diameter', color='#de2d26', linewidth=3)


    # Scatter plot data (values on x-axis and fixed y=0)
    #x_scatter = trial_df['End']
    #y_scatter = np.full((len(x_scatter)), 56)
    #colors = ['green' if trial_df['Correct'][i] == 1 else 'red' for i in range(len(x_scatter))]

    # Add scatter plot on the same figure
    #plt.scatter(x_scatter, y_scatter, s=50, edgecolor=colors, facecolors='none', label='Success')

    # Add labels, legend, and title
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.xlabel('Time (in min)', fontsize=20)
    plt.ylabel('Pupil Diameter (a.u.)', fontsize=20)
    plt.legend(fontsize=20)


