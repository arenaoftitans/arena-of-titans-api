from enum import Enum


class Color(Enum):
    BLACK = 'BLACK'
    BLUE = 'BLUE'
    RED = 'RED'
    YELLOW = 'YELLOW'
    ALL = 'ALL'


all_colors = set(Color)
all_colors.remove(Color['ALL'])


class ColorSet(set):
    """Set that contains values of the Color Enum.Color

    Convert string to the proper color on addition or update if necessary.
    """
    def __init__(self, colors=list()):
        super()
        self.update(colors)

    def update(self, colors):
        colors = [Color[color.upper()] if isinstance(color, str) else color for color in colors]
        if Color['ALL'] in colors:
            super().update(all_colors)
        else:
            super().update(colors)

    def add(self, color):
        # To ease unit testing
        if isinstance(color, str):  # pragma: no cover
            color = Color[color.upper()]
        if color == Color['ALL']:
            self.update([color])
        else:
            super().add(color)
