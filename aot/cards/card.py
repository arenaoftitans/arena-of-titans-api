from aot.board import Color


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
        print(new_squares)
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


class Card:
    _board = None
    _number_movements = 0
    _color = None
    _colors = set()
    _name = ''
    _movements = []
    movements_methods = {
        'line': _line_move,
        'diagonal': _diagonal_move
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
        self._colors = set(complementary_colors)
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
    def color(self):
        return self._color

    @property
    def name(self):
        return self._name
