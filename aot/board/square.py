from aot.board.color import Color


class Square:
    _x = 0
    _y = 0
    _color = None
    _occupied = False

    def __init__(self, x, y, color):
        self._x = x
        self._y = y
        if isinstance(color, str):
            self._color = Color[color.upper()]
        else:
            self._color = color

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def occupied(self):
        return self._occupied

    @occupied.setter
    def occupied(self, occupied):
        self._occupied = occupied

    @property
    def color(self):
        return self._color

    def __eq__(self, other):
        return type(other) == Square and\
            other._x == self._x and\
            other._y == self._y and\
            other._color == self._color

    def __str__(self):
        return 'Square({}, {}, {})'.format(self._x, self._y, self._color)

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return self._x * 10 + self._y * 100 + hash(self._color.name)


class SquareSet(set):
    _colors = set()

    def __init__(self, colors):
        super()
        self._colors = set()
        for color in colors:
            if isinstance(color, str):
                self._colors.add(Color[color.upper()])
            else:
                self._colors.add(color)

    def add(self, square):
        if square is not None and not square.occupied and \
                (square.color in self._colors or Color.ALL in self._colors):
            super().add(square)