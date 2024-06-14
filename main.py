import analysing_h5
from pathlib import Path
from eye_position import EyePosition, EyeVisualizer
filepath = Path("firstVideoDLC_resnet50_firstVersionMay23shuffle1_10000.h5")
filename = filepath
frame_rate = 30
total_frames = 16810
max_diameter = 48
min_diameter = 22

if __name__ == '__main__':
    eyes = EyePosition.create_eye_positions_from_h5(filename, True)
    for eye in eyes:
        eye.validate_diameter(min_diameter, max_diameter)
    eye_visualizer = EyeVisualizer(eyes, frame_rate)
    eye_visualizer.plot_pupil_diameter()
