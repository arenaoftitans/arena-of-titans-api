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

import logging

from aot.board import Square
from aot.utils import get_time


class LastAction:
    def __init__(
            self,
            description='',
            special_action=None,
            card=None,
            trump=None,
            player_name='',
            player_index=None,
            target_name=''):
        self.description = description
        self.player_name = player_name
        self.target_name = target_name
        self.player_index = player_index
        self.special_action = special_action
        self.card = card
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

    _ai_direction_aim = None
    _aim = set()
    _aim_min_x = 0
    _aim_max_x = 0
    _affecting_trumps = None
    _available_trumps = None
    _board = None
    _can_play = False
    _game_id = None
    _gauge = None
    _is_connected = False
    _current_square = None
    _deck = None
    _has_won = False
    _history = None
    _id = ''
    _index = -1
    _is_ai = False
    _last_action = None
    _last_square_previous_turn = None
    _name = ''
    _number_moves_to_play = 2
    _number_trumps_played = 0
    _number_turns_passed_not_connected = 0
    _rank = -1
    _special_action_start_time = 0
    _special_actions = None
    _special_actions_names = None
    _turn_start_time = 0

    def __init__(
            self,
            name,
            id,
            index,
            board,
            deck,
            gauge,
            trumps=None,
            hero='',
            is_ai=False,
    ):
        self._name = name
        self._id = id
        self._index = index
        self._hero = hero
        self._is_ai = is_ai
        self._board = board
        self._gauge = gauge

        self._affecting_trumps = []
        self._available_trumps = trumps if trumps is not None else []
        self._aim = self._generate_aim(board)
        self._ai_direction_aim = set([next(iter(self._aim))])
        self._current_square = board[
            self._index * self.BOARD_ARM_WIDTH_AND_MODULO,
            self.BOARD_ARM_LENGTH_AND_MAX_Y]
        self._current_square.occupied = True
        self._deck = deck
        self._has_won = False
        self._history = []
        self._number_moves_played = 0
        self._number_turns_passed_not_connected = 0
        self._rank = -1

    def _generate_aim(self, board):
        opposite_index = self._index + self.BOARD_ARM_WIDTH_AND_MODULO * \
            (1 if self._index >= self.BOARD_ARM_WIDTH_AND_MODULO else -1)
        aim_x = set()
        for i in range(self.BOARD_ARM_WIDTH_AND_MODULO):
            x = self.BOARD_ARM_WIDTH_AND_MODULO * opposite_index + i
            aim_x.add(self._board.correct_x(x))

        self._aim_max_x = max(aim_x)
        self._aim_min_x = min(aim_x)

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
        start_square = self.current_square

        if dest_square in possible_squares or not check_move:
            self._deck.play(card)
            self.move(dest_square)

        if card is not None:
            self._gauge.move(start_square, dest_square)
            self.last_action = LastAction(
                description='played_card',
                card=card.infos,
                player_name=self.name,
                player_index=self.index)
        else:
            self.last_action = LastAction(description='problem')

        if card is not None and card.special_actions is not None:
            self.special_actions = card.special_actions
            self._special_action_start_time = get_time()
            return True
        else:
            self._complete_action()
            self.special_actions = None
            return False

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

    def complete_special_actions(self):
        self._complete_action()

    def discard(self, card):
        self._deck.play(card)
        self.last_action = LastAction(
            description='dicarded_card',
            card=card.infos,
            player_name=self.name,
            player_index=self.index)
        self._complete_action()

    def pass_turn(self):
        if not self.is_connected and not self.is_ai:
            self._number_turns_passed_not_connected += 1
            logging.debug('Game n°{game_id}: player n°{id} ({name}) pass his/her turn '
                          'automatically (disconnected). {nb_passed}/{max_pass} before exclusion '
                          'from the game.'
                          .format(
                              game_id=self.game_id,
                              id=self.id,
                              name=self.name,
                              nb_passed=self._number_turns_passed_not_connected,
                              max_pass=self.MAX_NUMBER_TURN_EXPECTING_RECONNECT
                          ))

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

    def play_special_action(self, action, target=None, action_args=None):
        if action_args is None:
            action_args = {}

        if target is not None:
            action.affect(target, **action_args)
            self._special_actions_names.remove(action.name.lower())
            self.last_action = LastAction(
                description='played_special_action',
                special_action=action,
                player_name=self.name,
                target_name=target.name,
                player_index=self.index
            )

    def cancel_special_action(self, action):
        self._special_actions_names.remove(action.name.lower())

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
    def ai_aim(self):
        if self.on_aim_arm:
            return self.aim
        else:
            return self._ai_direction_aim

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
        return self._number_turns_passed_not_connected <= self.MAX_NUMBER_TURN_EXPECTING_RECONNECT

    @property
    def game_id(self):
        return self._game_id

    @game_id.setter
    def game_id(self, value):
        self._game_id = value

    @property
    def hand(self):
        return self._deck.hand

    @property
    def hand_for_debug(self):
        return list(map(lambda card: '{} {}'.format(card.name, card.color), self.hand))

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
    def is_ai(self):
        return self._is_ai

    @property
    def is_connected(self):
        return self._is_connected

    @is_connected.setter
    def is_connected(self, value):
        if value:
            self._number_turns_passed_not_connected = 0
        self._is_connected = value

    @property
    def on_aim_arm(self):
        return self._board.is_in_arm(self._current_square) and \
            self._aim_min_x <= self._current_square.x <= self._aim_max_x

    @property
    def last_action(self):  # pragma: no cover
        return self._last_action

    @last_action.setter
    def last_action(self, value):
        self._last_action = value
        self._history.append(value)

    @property
    def has_special_actions(self):
        return self._special_actions_names is not None and len(self._special_actions_names) > 0

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
    def special_action_start_time(self):
        return self._special_action_start_time

    @property
    def special_actions(self):
        return self._special_actions

    @special_actions.setter
    def special_actions(self, actions):
        if actions is not None:
            self._special_actions_names = [action.name.lower() for action in actions]
            self._special_actions = actions
            self._special_actions.set_additionnal_arguments(board=self._board)

    @property
    def name_next_special_action(self):
        return next(iter(self._special_actions_names))

    @property
    def still_in_game(self):
        if self.is_ai:
            return not self.has_won
        else:
            return not self.has_won and (self.is_connected or self.expect_reconnect)

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
