import json
from aot.board import Board


class Game:
    _board = None
    _player = None

    def create(self, player_name):
        with open('aot/resources/games/standard.json') as games:
            game = json.load(games)
        self._board = Board(game['board'])
        deck = Deck(self._board, game)
        self._player = Player(player_name, deck, self._board[0, 0])

    def view_possible_squares(self, card):
        return self._player.view_possible_squares(card)

    def play(self, card, square):
        return self._player.play(card, square)

    @property
    def player_name(self):
        return self._player.name
