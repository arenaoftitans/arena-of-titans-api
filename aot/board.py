from aot.color import Color


class Board:
    _board = []
    _x_max = 0
    _y_max = 0

    def __init__(self, board_description):
        self._create_board(board_description)

    def _create_board(self, board_description):
        self._board = []
        x, y = 0, 0
        for line in board_description:
            line_board = []
            x = 0
            for color in line.split(','):
                line_board.append(Square(x, y, color))
                x += 1
            self._board.append(line_board)
            y += 1
        self._x_max = len(self._board[0])
        self._y_max = len(self._board)

    def get_line_squares(self, square, color):
        squares = SquareSet(color)
        squares.add(self._get_square(square.x - 1, square.y))
        squares.add(self._get_square(square.x + 1, square.y))
        squares.add(self._get_square(square.x, square.y - 1))
        squares.add(self._get_square(square.x, square.y + 1))
        return squares

    def get_diagonal_squares(self, square, color):
        squares = SquareSet(color)
        squares.add(self._get_square(square.x - 1, square.y - 1))
        squares.add(self._get_square(square.x + 1, square.y - 1))
        squares.add(self._get_square(square.x - 1, square.y + 1))
        squares.add(self._get_square(square.x + 1, square.y + 1))
        return squares

    def _get_square(self, x, y):
        while x < 0:
            x += self._x_max
        if 0 <= y and y < self._y_max:
            return self._board[y][x % self._x_max]

    def __len__(self):
        return len(self._board) * len(self._board[0])

    def __getitem__(self, coords):
        if isinstance(coords, tuple):
            x, y = coords
            return self._board[y][x]
        else:
            return self._board[coords]


class SquareSet(set):
    def __init__(self, color):
        super()
        if isinstance(color, str):
            self._color = Color[color]
        else:
            self._color = color

    def add(self, element):
        if element is not None and element.color == self._color:
            super().add(element)


class Square:
    _x = 0
    _y = 0
    _color = None

    def __init__(self, x, y, color):
        self._x = x
        self._y = y
        if isinstance(color, str):
            self._color = Color[color.lower()]

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

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
