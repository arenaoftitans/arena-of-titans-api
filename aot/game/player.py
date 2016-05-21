from aot.board import Square
from time import time


class LastAction:
    def __init__(self, description='', card=None, trump=None, player_name=''):
        self.description = description
        self.player_name = player_name
        if card is None:
            self.card = {}
        else:
            self.card = card
        if trump is None:
            self.trump = {}
        else:
            self.trump = trump


class Player:
    BOARD_ARM_WIDTH_AND_MODULO = 4
    BOARD_ARM_LENGTH_AND_MAX_Y = 8
    MAX_NUMBER_AFFECTING_TRUMPS = 4
    MAX_NUMBER_MOVE_TO_PLAY = 2
    MAX_NUMBER_TRUMPS_PLAYED = 1

    _aim = set()
    _affecting_trumps = None
    _available_trumps = None
    _board = None
    _can_play = False
    _is_connected = False
    _current_square = None
    _deck = None
    _has_won = False
    _id = ''
    _index = -1
    _last_action = None
    _last_square_previous_turn = None
    _name = ''
    _number_moves_to_play = 2
    _number_trumps_played = 0
    _rank = -1
    _turn_start_time = 0

    def __init__(self, name, id, index, board, deck, trumps=None, hero=''):
        self._name = name
        self._id = id
        self._index = index
        self._hero = hero

        self._affecting_trumps = []
        self._available_trumps = trumps if trumps is not None else []
        self._aim = self._generate_aim(board)
        self._board = board
        self._current_square = board[
            self._index * self.BOARD_ARM_WIDTH_AND_MODULO,
            self.BOARD_ARM_LENGTH_AND_MAX_Y]
        self._current_square.occupied = True
        self._deck = deck
        self._has_won = False
        self._number_moves_played = 0
        self._rank = -1

    def _generate_aim(self, board):
        opposite_index = self._index + self.BOARD_ARM_WIDTH_AND_MODULO * \
            (1 if self._index >= self.BOARD_ARM_WIDTH_AND_MODULO else -1)
        aim_x = set()
        for i in range(self.BOARD_ARM_WIDTH_AND_MODULO):
            aim_x.add(self.BOARD_ARM_WIDTH_AND_MODULO * opposite_index + i)

        return set([board[x, self.BOARD_ARM_LENGTH_AND_MAX_Y] for x in aim_x])

    def view_possible_squares(self, card):
        return self._deck.view_possible_squares(card, self._current_square)

    def get_card(self, card_name, card_color):
        return self._deck.get_card(card_name, card_color)

    def can_move(self, card, square):
        return square in self._deck.view_possible_squares(card, self._current_square)

    def play_card(self, card, square, check_move=True):
        if not card and check_move:
            return

        possible_squares = self._get_possible_squares(card, check_move)
        dest_square = self._get_dest_square(square)

        if dest_square in possible_squares or not check_move:
            self._deck.play(card)
            self.move(dest_square)

        if card is not None:
            self._last_action = LastAction(
                description='played a card',
                card=card.infos,
                player_name=self.name)
        else:
            self._last_action = LastAction(description='A problem occured')
        self._complete_action()

    def _get_possible_squares(self, card, check_move):
        if card and check_move:
            return self.view_possible_squares(card)
        else:
            return set()

    def _get_dest_square(self, square):
        if square is not None and not isinstance(square, Square):
            x, y = square
            return self._board[x, y]
        else:
            return square

    def _complete_action(self):
        self._number_moves_played += 1
        self._can_play = self._number_moves_played < self._number_moves_to_play
        if not self.can_play:
            self._deck.init_turn()

    def discard(self, card):
        self._deck.play(card)
        self._last_action = LastAction(
            description='dicarded a card',
            card=card.infos,
            player_name=self.name)
        self._complete_action()

    def pass_turn(self):
        self._last_action = LastAction(
            description='passed his/her turn',
            player_name=self.name)
        self._can_play = False
        self._deck.init_turn()

    def move(self, square):
        if square is None:
            return
        if self._current_square is not None:
            self._current_square.occupied = False
        self._current_square = square
        self._current_square.occupied = True

    def wins(self, rank=-1):
        if rank > 0:
            self._has_won = True
        self._rank = rank

    def init_turn(self):
        self._turn_start_time = int(time() * 1000)
        self._number_moves_played = 0
        self._number_trumps_played = 0
        self._can_play = True
        self._last_square_previous_turn = self._current_square
        self._enable_trumps()

    def _enable_trumps(self):
        for trump in self._affecting_trumps:
            trump.affect(self)

    def complete_turn(self):
        self._revert_to_default()
        for trump in self._affecting_trumps:
            trump.consume()

        for trump in self._affecting_trumps:
            if trump.duration == 0:
                self._affecting_trumps.remove(trump)

    def _revert_to_default(self):
        self._deck.revert_to_default()
        self._number_moves_to_play = self.MAX_NUMBER_MOVE_TO_PLAY

    def modify_number_moves(self, delta):
        self._number_moves_to_play += delta

    def _affect_by(self, trump):
        if len(self._affecting_trumps) < self.MAX_NUMBER_AFFECTING_TRUMPS:
            self._affecting_trumps.append(trump)
            if self._can_play:
                trump.affect(self)
            return True
        else:
            return False

    def get_trump(self, trump_name):
        return self._available_trumps[trump_name]

    def play_trump(self, trump, target=None):
        if self.can_play_trump and target is not None:
            if target._affect_by(trump):
                self._number_trumps_played += 1
                description = ('{my_name} just played a trump on {target_name}'
                               .format(my_name=self.name, target_name=target.name))
                self._last_action = LastAction(
                    description=description,
                    trump=trump,
                    player_name=self.name)
                return True
            else:
                return False
        else:
            return False

    def __str__(self):  # pragma: no cover
        return 'Player(id={id}, name={name}, index={index})'\
            .format(id=self.id, name=self.name, index=self.index)

    def __repr__(self):  # pragma: no cover
        return str(self)

    @property
    def _is_on_last_line(self):
        return self._current_square in self._aim

    @property
    def _was_on_last_line_previous_move(self):
        return self._last_square_previous_turn in self._aim

    @property
    def affecting_trumps(self):
        return self._affecting_trumps

    @property
    def aim(self):
        return self._aim

    @property
    def can_play(self):
        return self._can_play

    @can_play.setter
    def can_play(self, value):
        self._can_play = bool(value)

    @property
    def can_play_trump(self):
        return self.can_play and self._number_trumps_played < self.MAX_NUMBER_TRUMPS_PLAYED

    @property
    def current_square(self):
        return self._current_square

    @property
    def deck(self):
        return self._deck

    @property
    def hand(self):
        return self._deck.hand

    @property
    def hero(self):
        return self._hero

    @property
    def id(self):  # pragma: no cover
        return self._id

    @property
    def index(self):
        return self._index

    @property
    def is_connected(self):
        return self._is_connected

    @is_connected.setter
    def is_connected(self, value):
        self._is_connected = value

    @property
    def last_action(self):  # pragma: no cover
        return self._last_action

    @property
    def last_square_previous_turn(self):
        return self._last_square_previous_turn

    @property
    def has_reached_aim(self):
        return self._is_on_last_line and self._was_on_last_line_previous_move

    @property
    def has_won(self):
        return self._has_won

    @property
    def name(self):
        return self._name

    @property
    def rank(self):
        return self._rank

    @property
    def turn_start_time(self):
        return self._turn_start_time

    @property
    def trumps(self):
        return [
            {
                "name": trump.args['name'],
                "description": trump.args['description'],
                "duration": trump.args['duration'],
                "cost": trump.args['cost'],
                "must_target_player": trump.args['must_target_player']
            } for trump in self._available_trumps]
