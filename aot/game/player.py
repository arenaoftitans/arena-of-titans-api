################################################################################
# Copyright (C) 2015-2016 by Arena of Titans Contributors.
#
# This file is part of Arena of Titans.
#
# Arena of Titans is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Arena of Titans is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
################################################################################

from aot.board import Square
from aot.game.ai import (
    find_cheapest_card,
    find_move_to_play,
)
from aot.utils import get_time


class LastAction:
    def __init__(
            self, description='',
            card=None,
            trump=None,
            player_name='',
            player_index=None,
            target_name=''):
        self.description = description
        self.player_name = player_name
        self.target_name = target_name
        self.player_index = player_index
        if card is None:
            self.card = None
        else:
            self.card = card
        if trump is None:
            self.trump = None
        else:
            self.trump = trump


class Player:
    BOARD_ARM_WIDTH_AND_MODULO = 4
    BOARD_ARM_LENGTH_AND_MAX_Y = 8
    MAX_NUMBER_AFFECTING_TRUMPS = 4
    MAX_NUMBER_MOVE_TO_PLAY = 2
    MAX_NUMBER_TRUMPS_PLAYED = 1
    #: Maximum number of turn the game will pass before considering that the player will never
    # reconnect and not take him/her into account in the remaining players.
    MAX_NUMBER_TURN_EXPECTING_RECONNECT = 4

    _aim = set()
    _affecting_trumps = None
    _available_trumps = None
    _board = None
    _can_play = False
    _is_connected = False
    _current_square = None
    _deck = None
    _has_won = False
    _history = None
    _id = ''
    _index = -1
    _last_action = None
    _last_square_previous_turn = None
    _name = ''
    _number_moves_to_play = 2
    _number_trumps_played = 0
    _number_turn_passed_not_connected = 0
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
        self._ai_aim = next(iter(self._aim))
        self._board = board
        self._current_square = board[
            self._index * self.BOARD_ARM_WIDTH_AND_MODULO,
            self.BOARD_ARM_LENGTH_AND_MAX_Y]
        self._current_square.occupied = True
        self._deck = deck
        self._has_won = False
        self._history = []
        self._number_moves_played = 0
        self._number_turn_passed_not_connected = 0
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
            self.last_action = LastAction(
                description='played_card',
                card=card.infos,
                player_name=self.name,
                player_index=self.index)
        else:
            self.last_action = LastAction(description='problem')
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

    def play_auto(self):
        while self.can_play:
            card, square = find_move_to_play(
                self.hand,
                self.current_square,
                self._ai_aim,
                self._board
            )
            if card:
                self.play_card(card, square)
            else:
                cheapest_card = find_cheapest_card(self.hand)
                self.discard(cheapest_card)

    def discard(self, card):
        self._deck.play(card)
        self.last_action = LastAction(
            description='dicarded_card',
            card=card.infos,
            player_name=self.name,
            player_index=self.index)
        self._complete_action()

    def pass_turn(self):
        if not self.is_connected:
            self._number_turn_passed_not_connected += 1

        self.last_action = LastAction(
            description='passed_turn',
            player_name=self.name,
            player_index=self.index)
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
        self._turn_start_time = get_time()
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

        self._remove_consumed_trumps()

    def _remove_consumed_trumps(self):
        # If we modify the size of the size while looping on it, we will skip some element. For
        # instance if two elements are consumed in the list, only the first one will be removed.
        to_remove = set()
        for trump in self._affecting_trumps:
            if trump.duration <= 0:
                to_remove.add(trump)

        for trump in to_remove:
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
                self.last_action = LastAction(
                    description='played_trump',
                    trump=trump,
                    player_name=self.name,
                    target_name=target.name,
                    player_index=self.index)
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
    def on_last_line(self):
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
    def expect_reconnect(self):
        return self._number_turn_passed_not_connected <= self.MAX_NUMBER_TURN_EXPECTING_RECONNECT

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
        if value:
            self._number_turn_passed_not_connected = 0
        self._is_connected = value

    @property
    def last_action(self):  # pragma: no cover
        return self._last_action

    @last_action.setter
    def last_action(self, value):
        self._last_action = value
        self._history.append(value)

    @property
    def last_square_previous_turn(self):
        return self._last_square_previous_turn

    @property
    def has_reached_aim(self):
        return self.on_last_line and self._was_on_last_line_previous_move

    @property
    def has_won(self):
        return self._has_won

    @property
    def history(self):
        return self._history

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
