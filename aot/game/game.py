import json
from aot.board import Board
from aot.cards import Card
from aot.board import Color


class Game:
    _board = None
    _player = None

    def create(self, player_name):
        with open('games.json') as games:
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


class Player:
    _deck = None
    _name = ''
    _position = None

    def __init__(self, name, deck, original_position):
        self._name = name
        self._deck = deck
        self._position = original_position

    def view_possible_squares(self, card):
        return self._deck.view_possible_squares(card, self._position)

    def play(self, card, square):
        possible_squares = self.view_possible_squares(card)
        x, y = square
        dest_square = self._deck.board[x, y]
        if dest_square in possible_squares:
            self._position = dest_square
            return dest_square

    @property
    def name(self):
        return self._name


class Deck:
    _board = None
    _deck = []

    def __init__(self, board, game):
        self._board = board
        self._create_deck(game)

    def _create_deck(self, game):
        self._deck = []
        for color in game['colors']:
            for card in game['cards']:
                self._deck.append(
                    Card(self._board, color=Color[color.upper()], **card)
                )

    def view_possible_squares(self, card, position):
        card_name, card_color = card
        game_card = self._get_card(card_name, card_color)
        return game_card.move(position)

    def _get_card(self, card_name, card_color):
        if isinstance(card_color, str):
            card_color = Color[card_color]
        matching_cards = [card for card in self._deck
                          if card.name == card_name and
                          card.color == card_color]

        assert len(matching_cards) == 1
        return matching_cards[0]

    @property
    def board(self):
        return self._board
