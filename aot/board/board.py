from aot.board.square import (
    Square,
    SquareSet
    )


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
        squares.add(self[square.x - 1, square.y])
        squares.add(self[square.x + 1, square.y])
        squares.add(self[square.x, square.y - 1])
        squares.add(self[square.x, square.y + 1])
        return squares

    def get_diagonal_squares(self, square, color):
        squares = SquareSet(color)
        squares.add(self[square.x - 1, square.y - 1])
        squares.add(self[square.x + 1, square.y - 1])
        squares.add(self[square.x - 1, square.y + 1])
        squares.add(self[square.x + 1, square.y + 1])
        return squares

    def __len__(self):
        return len(self._board) * len(self._board[0])

    def __getitem__(self, coords):
        x, y = coords
        while x < 0:
            x += self._x_max
        if 0 <= y and y < self._y_max:
            return self._board[y][x % self._x_max]
