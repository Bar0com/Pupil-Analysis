from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
import numpy
from loguru import logger

from eye_direction import EyeDirection


class EyePosition:
    def __init__(self, north: EyeDirection, south: EyeDirection, west: EyeDirection, east: EyeDirection) -> None:
        self.north: EyeDirection = north
        self.south: EyeDirection = south
        self.west: EyeDirection = west
        self.east: EyeDirection = east
        self.diameter = self.calculate_pupil_diameter()
        self.valid = True

    @classmethod
    def create_eye_positions_from_h5(cls, filepath: Path, from_pickle=False) -> list[EyePosition]:
        df = pd.read_hdf(filepath)
        df = df.droplevel(0, axis=1)
        eye_positions = []
        for index, row in df.iterrows():
            eye_direction_north = EyeDirection(row['EyeNorth']['x'], row['EyeNorth']['y'],
                                               row['EyeNorth']['likelihood'], "NORTH")
            eye_direction_south = EyeDirection(row['EyeSouth']['x'], row['EyeSouth']['y'],
                                               row['EyeSouth']['likelihood'], "SOUTH")
            eye_direction_west = EyeDirection(row['EyeWest']['x'], row['EyeWest']['y'],
                                              row['EyeWest']['likelihood'], "WEST")
            eye_direction_east = EyeDirection(row['EyeEast']['x'], row['EyeEast']['y'],
                                              row['EyeEast']['likelihood'], "EAST")
            e = EyePosition(eye_direction_north, eye_direction_south, eye_direction_west, eye_direction_east)
            eye_positions.append(e)
        return eye_positions

    def calculate_pupil_diameter(self):
        diameter = (numpy.sqrt((self.north.x - self.south.x) ** 2 + (self.north.y - self.south.y) ** 2) +
                    numpy.sqrt((self.west.x - self.east.x) ** 2 + (self.west.y - self.east.y) ** 2)) / 2
        return diameter

    def get_minimum_likelihood(self):
        return min(self.north.likelihood, self.south.likelihood, self.west.likelihood, self.east.likelihood)

    def validate_diameter(self, min: int, max: int):
        outlier_condition = (self.diameter < min) | (self.diameter > max)
        if outlier_condition:
            self.valid = False
            logger.debug("Invalid EyePosition found.")
