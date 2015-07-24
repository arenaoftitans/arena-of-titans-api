from aot.board import Color
from aot.board import ColorSet
from aot.board import Square


def _line_move(board, origin, number_movements_left, possible_squares, colors):
    if number_movements_left > 0:
        new_squares = board.get_line_squares(origin, colors)
        for new_square in new_squares:
            if new_square not in possible_squares:
                _line_move(
                    board,
                    new_square,
                    number_movements_left - 1,
                    possible_squares,
                    colors
                )
        possible_squares.update(new_squares)


def _diagonal_move(
        board,
        origin,
        number_movements_left,
        possible_squares,
        colors):
    if number_movements_left > 0:
        new_squares = board.get_diagonal_squares(origin, colors)
        for new_square in new_squares:
            if new_square not in possible_squares:
                _diagonal_move(
                    board,
                    new_square,
                    number_movements_left - 1,
                    possible_squares,
                    colors
                )
        possible_squares.update(new_squares)


def _knight_move(
        board,
        origin,
        number_movements_left,
        possible_squares,
        colors):
    if number_movements_left > 0:
        temporary_vertical_squares = set([
            Square(origin.x, origin.y + 2, 'all'),
            Square(origin.x, origin.y - 2, 'all'),
        ])

        probable_squares = set()
        for square in temporary_vertical_squares:
            right_square = board[square.x + 1, square.y, 'right']
            left_square = board[square.x - 1, square.y, 'left']
            if right_square:
                probable_squares.add(right_square)
            if left_square:
                probable_squares.add(left_square)

        possible_squares.update([square for square in probable_squares
                                 if square.color in colors
                                 and not square.occupied])

        square_left = board[origin.x - 1, origin.y, 'left']
        square_right = board[origin.x + 1, origin.y, 'right']
        temporary_horizontal_squares = set()
        if square_left:
            temporary_horizontal_squares.add(board[square_left.x - 1, square_left.y, 'left'])
        if square_right:
            temporary_horizontal_squares.add(board[square_right.x + 1, square_right.y, 'right'])
        probable_squares = set()
        for square in temporary_horizontal_squares:
            if not square:
                continue
            up_square = board[square.x, square.y + 1]
            down_square = board[square.x, square.y - 1]
            if up_square:
                probable_squares.add(up_square)
            if down_square:
                probable_squares.add(down_square)

        possible_squares.update([square for square in probable_squares
                                 if square.color in colors
                                 and not square.occupied])


class Card:
    _board = None
    _number_movements = 0
    _color = None
    _colors = set()
    _name = ''
    _movements = []
    movements_methods = {
        'line': _line_move,
        'diagonal': _diagonal_move,
        'knight': _knight_move,
    }

    def __init__(
        self,
        board,
        number_movements=1,
        color=Color['ALL'],
        complementary_colors=set(),
        name='',
        movements_types=list()
    ):
        self._board = board
        self._number_movements = number_movements
        self._color = color
        self._colors = ColorSet(complementary_colors)
        self._colors.add(color)
        self._name = name
        self._movements = [
            self.movements_methods[mvt] for mvt in movements_types
        ]

    def move(self, origin):
        return self._move(origin, self._number_movements, set())

    def _move(self, origin, number_movements_left, possible_squares):
        for move in self._movements:
            move(
                self._board,
                origin,
                number_movements_left,
                possible_squares,
                self._colors
            )
        return possible_squares

    @property
    def color(self): # pragma: no cover
        return self._color

    @property
    def name(self): # pragma: no cover
        return self._name
