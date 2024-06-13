import analysing_h5

filename = r"D:\OneDrive\Documents\University of Amsterdam\Internship\DeepLabCutData\firstVideoDLC_resnet50_firstVersionMay23shuffle1_10000.h5"
frame_rate = 30
total_frames = 16810
max_diameter = 48
min_diameter = 22

if __name__ == '__main__':
    source_data = analysing_h5.read_in_h5(filename)
    pupil_diameter_df = analysing_h5.calculate_pupil_diameter(source_data)
    pupil_diameter_df = analysing_h5.add_timestamps(pupil_diameter_df, frame_rate, total_frames)
    outliers = analysing_h5.identify_diameter_outliers(pupil_diameter_df, max_diameter, min_diameter)
    clean_pupil_diameter_df = analysing_h5.drop_outliers(pupil_diameter_df, outliers)
    # Drop start data, still need to re-train model: analysing_h5.drop_start_data()
    analysing_h5.plot_pupil_diameter(clean_pupil_diameter_df)
    print(clean_pupil_diameter_df.head(n=10).to_string(index=False))
