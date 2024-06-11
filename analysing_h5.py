import h5py
import pandas as pd
import numpy
import matplotlib.pyplot as plt

filename = r"C:\Users\flori\OneDrive\Documents\University of Amsterdam\Internship\DeepLabCutData\firstVideoDLC_resnet50_firstVersionMay23shuffle1_10000.h5"


h5_df = pd.read_hdf(filename)
h5_df = h5_df.droplevel(0, axis=1)

# Accessing x and y data for EyeNorth
eye_north_x = h5_df['EyeNorth']['x']
eye_north_y = h5_df['EyeNorth']['y']
eye_north_likelihood = h5_df['EyeNorth']['likelihood']

# Accessing x and y data for EyeSouth
eye_south_x = h5_df['EyeSouth']['x']
eye_south_y = h5_df['EyeSouth']['y']
eye_south_likelihood = h5_df['EyeSouth']['likelihood']

# Accessing x and y data for EyeWest
eye_west_x = h5_df['EyeWest']['x']
eye_west_y = h5_df['EyeWest']['y']
eye_west_likelihood = h5_df['EyeWest']['likelihood']

# Accessing x and y data for EyeEast
eye_east_x = h5_df['EyeEast']['x']
eye_east_y = h5_df['EyeEast']['y']
eye_east_likelihood = h5_df['EyeEast']['likelihood']


# Calculating pupil diameter and writing it in a list
diameter_df = []
for i in range(len(h5_df.index)):
    d = (numpy.sqrt((eye_north_x[i] - eye_south_x[i])**2 + (eye_north_y[i] - eye_south_y[i])**2) +
         numpy.sqrt((eye_west_x[i] - eye_east_x[i])**2 + (eye_west_y[i] - eye_east_y[i])**2)) / 2
    diameter_df.append(d)

# Adding the diameter list to the original Dataframe
h5_df['EyeTotal', 'Diameter'] = diameter_df

# Some fun calculations with the diameter
#std = h5_df['EyeTotal', 'Diameter'].std()
#pre_mean = h5_df['EyeTotal', 'Diameter'].mean()
#pre_min = h5_df['EyeTotal', 'Diameter'].min()
#pre_max = h5_df['EyeTotal', 'Diameter'].max()

# Outlier detection based on "arbitrary" borders and creation of a cleaned DF by excluding outliers
outlier_condition = (h5_df['EyeTotal', 'Diameter'] < 22) | (h5_df['EyeTotal', 'Diameter'] > 48)
outlier_values = h5_df.loc[outlier_condition, ('EyeTotal', 'Diameter')]
clean_df = h5_df.drop(index= outlier_values.index)
print(clean_df.head(n=10).to_string(index=False))


# Plotting the Diameter over time
graph = clean_df.loc[:, ('EyeTotal', 'Diameter')].plot.line()
graph.plot()
plt.show()

#graph = h5_df.loc[:, ('EyeTotal', 'Diameter')].plot.line()
graph.plot()
plt.show()



