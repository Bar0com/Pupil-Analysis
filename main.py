import numpy as np
import matplotlib.pyplot as plt
import pandas
import pandas as pd

import analysing_h5 as h5
import hidden_markov_model as hmm
from hmmlearn import hmm as hidmm

# FOR FINAL EXPERIMENTS:
    # 1. currently the LED is on for up to 5.7s but for the final experiment we can hardcode that after trial onset the
    # maximum time of a trial will be 2s
    # 2. for the final experiments also the last X amount of trials will be deleted (5, 10 or 15 or smth), this will
    # later also be hard coded
    # 3. Before Stimulus onset we look at the baseline that is Stimulus onset - 3s, so we will hardcode -3s before
    # stimulus onset as the baseline
    # 4. The order of info from the behavioural data file is hardcoded right now, it needs to be checked if the order
    # remains the same before using it, also: LeftLick = 1, RightLick = 2 in the file (first Column)

# IDEA:
    # create plot containing the pupil diameter over the trial duration for all trials, overlaying all trials
    # into one plot


# filename = r"D:\OneDrive\Documents\University of Amsterdam\Internship\DeepLabCutData\firstVideoDLC_resnet50_firstVersionMay23shuffle1_10000.h5"
filename = r'C:\Users\flori\OneDrive\Documents\University of Amsterdam\Internship\DeepLabCutData\Video_02_06_24_croppedDLC_resnet50_secondVersionJun13shuffle1_26000.h5'
file_behav_data = r'C:\Users\flori\PycharmProjects\DeepLabCut_v1\behav_performance.csv'
frame_rate = 30
total_frames = 117456
max_diameter = 55
min_diameter = 22
unimportant_columns = ['EyeNorth', 'EyeSouth', 'EyeWest', 'EyeEast', 'EyeLidNorth', 'EyeLidSouth']


if __name__ == '__main__':
    # reading in h5 data and behavioural data and making small adjustments to the format
    source_data = h5.read_in_h5(filename)
    behav_results = h5.read_in_behav(file_behav_data)

    # calculating pupil diameter and coding the direction of the lick and adding it to df
    pupil_diameter_df = h5.calculate_pupil_diameter(source_data)
    behav_results = h5.code_lick_direction(behav_results)

    # adding timestamps column to diameter df
    pupil_diameter_df = h5.add_timestamps(pupil_diameter_df, frame_rate, total_frames)

    # identify and remove outliers and drop columns that are no longer needed
    outliers = h5.identify_diameter_outliers(pupil_diameter_df, max_diameter, min_diameter)
    clean_pupil_diameter_df = h5.drop_outliers(pupil_diameter_df, outliers)
    clean_pupil_diameter_df = h5.drop_unimportant_columns(clean_pupil_diameter_df, unimportant_columns)

    # smoothing the pupil diameter data, plotting it and adding it to the pupil-diameter df
    diameter_signal_smooth = h5.smoothing_savitzky_golay(np.array(clean_pupil_diameter_df['EyeTotal']['Diameter']), 50, 2)
    fig, ax = plt.subplots()
    #diameter_plot_normal = h5.plot_pupil_diameter(clean_pupil_diameter_df, ax)
    smooth_df = h5.merge_smoothed_data(clean_pupil_diameter_df, diameter_signal_smooth)
    #diameter_plot_smooth = h5.plot_smooth_graph(clean_pupil_diameter_df, diameter_signal_smooth, ax)

    # breaking down the entire dataset into trials based on likelihood of LED
    trial_data = h5.break_into_trials(smooth_df)
    trial_data = h5.estimate_baseline(smooth_df, trial_data)
    trial_data = h5.add_performance_data(trial_data, behav_results)
    #performance_plot = h5.plot_performance_graph(trial_data, smooth_df, ax)
    #plt.show()
    #print(trial_data.to_string())

    # building hmm
    hmm_data = hmm.create_tuple(trial_data)
    hmm_model = hmm.define_model()
    hmm_model = hmm.fit_model(hmm_model, hmm_data)
    hmm_hidden_states = hmm.predict_hidden_states(hmm_model, hmm_data)
    hmm_analyze = hmm.analyze_results(trial_data, hmm_hidden_states)
