from direction import Direction


class EyeDirection:
    def __init__(self, x: float, y: float, likelihood: float, direction: str) -> None:
        self.x = x
        self.y = y
        self.likelihood = likelihood
        self.direction = Direction[direction]