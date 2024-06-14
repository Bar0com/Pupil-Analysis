import matplotlib.pyplot as plt
from eye_position import EyePosition

class EyeVisualizer:
    def __init__(self, eye_positions: list[EyePosition], framerate: int) -> None:
        self.eye_positions = eye_positions
        self.framerate = framerate

    def plot_pupil_diameter(self, validated_only=True) -> None:
        # Plotting the Diameter over time
        plot_table = []
        for i, eye_position in enumerate(self.eye_positions):
            timestamp = self._get_timestamps_minutes(i)
            eye_stamp = [timestamp, eye_position.diameter]
            if not validated_only:
                plot_table.append(eye_stamp)
            elif eye_position.valid:
                plot_table.append(eye_stamp)
        x_values = [row[0] for row in plot_table]
        y_values = [row[1] for row in plot_table]

        # Plotting the data
        plt.figure(figsize=(10, 6))
        plt.plot(x_values, y_values, marker='o')

        # Adding title and labels
        plt.title('2D Data Plot')
        plt.xlabel('X values')
        plt.ylabel('Y values')

        # Display the plot
        plt.grid(True)
        plt.show()

    def _get_timestamps_minutes(self, frame_counter: int) -> float:
        timestamp = frame_counter / self.framerate / 60
        return timestamp

    # NOT RELEVANT
    def drop_start_data(data_df, likelihood_threshold):
        for i in range(len(data_df['LED']['likelihood'])):
            if data_df['LED']['likelihood'][i] > likelihood_threshold:
                data_df.loc[0:i - 1].drop()
                return data_df
        print("No start data was dropped")
