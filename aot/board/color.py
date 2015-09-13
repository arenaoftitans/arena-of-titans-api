from enum import Enum


class Color(Enum):
    BLACK = 'BLACK'
    BLUE = 'BLUE'
    RED = 'RED'
    YELLOW = 'YELLOW'
    ALL = 'ALL'


class ColorSet(set):
    """Set that contains values of the Color Enum.Color

    Convert string to the proper color on addition or update if necessary.
    """
    def __init__(self, colors):
        super()
        self.update(colors)

    def update(self, colors):
        for color in colors:
            self.add(color)

    def add(self, color):
        # To ease unit testing
        if isinstance(color, str):  # pragma: no cover
            color = Color[color.upper()]
        super().add(color)
