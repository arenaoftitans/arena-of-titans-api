#
#  Copyright (C) 2015-2020 by Arena of Titans Contributors.
#
#  This file is part of Arena of Titans.
#
#  Arena of Titans is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Arena of Titans is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
#

import daiquiri

from . import trumps as imported_trumps
from .board import Square
from .exceptions import NotYourTurnError
from .utils import get_time


class LastAction:
    def __init__(
        self,
        description="",
        special_action=None,
        card=None,
        trump=None,
        player_name="",
        player_index=None,
        target_name="",
        target_index=None,
    ):
        self.description = description
        self.player_name = player_name
        self.target_name = target_name
        self.target_index = target_index
        self.player_index = player_index
        self.special_action = special_action
        self.card = card
        self.trump = trump


class Player:
    MAX_NUMBER_AFFECTING_TRUMPS = 4
    MAX_NUMBER_MOVE_TO_PLAY = 2
    MAX_NUMBER_TRUMPS_PLAYED = 1
    #: Maximum number of turn the game will pass before considering that the player will never
    # reconnect and not take him/her into account in the remaining players.
    MAX_NUMBER_TURN_EXPECTING_RECONNECT = 4
    LOGGER = daiquiri.getLogger(__name__)

    _aim = set()
    _aim_min_x = 0
    _aim_max_x = 0
    _trump_effects = None
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
    _id = ""
    _index = -1
    _is_ai = False
    _last_action = None
    _last_square_previous_turn = None
    _name = ""
    _number_moves_to_play = 2
    _number_trumps_played = 0
    _number_turns_passed_not_connected = 0
    _power = None
    _rank = -1
    _special_action_start_time = 0
    _special_actions = None
    _special_actions_names = None
    _turn_start_time = 0

    def __init__(
        self, name, id_, index, board, deck, gauge, trumps=None, hero="", is_ai=False, power=None,
    ):
        self._name = name
        self._id = id_
        self._index = index
        self._hero = hero
        self._is_ai = is_ai
        self._board = board
        self._gauge = gauge

        self._trump_effects = []
        self._aim = board.aim
        self._current_square = board.get_square_for_player_with_index(index)
        self._current_square.occupied = True
        self._deck = deck
        self._has_won = False
        self._history = []
        self._number_moves_played = 0
        self._number_turns_passed_not_connected = 0
        self._power = power or imported_trumps.VoidPower()
        self._available_trumps = self._power.setup(trumps or ())
        self._rank = -1

    def setup_new_power(self, power):
        # This is to correctly enable stolen power. They will be teardowned as part of the normal
        # trump effect process.
        self._available_trumps = power.setup(self._available_trumps)

    def view_possible_squares(self, card):
        return self._deck.view_possible_squares(card, self._current_square)

    def get_card(self, card_name, card_color):
        return self._deck.get_card(card_name, card_color)

    def can_move(self, card, square):
        return square in self._deck.view_possible_squares(card, self._current_square)

    def play_card(self, card, square, check_move=True):
        if not card and check_move:
            return
        elif not self.has_remaining_moves_to_play:
            return

        possible_squares = self._get_possible_squares(card, check_move)
        dest_square = self._get_dest_square(square)
        start_square = self.current_square

        if dest_square in possible_squares or not check_move:
            self._deck.play(card)
            self.move(dest_square)

        if card is not None:
            self._gauge.move(start_square, dest_square, card)
            self.last_action = LastAction(
                description="played_card",
                card=card.infos,
                player_name=self.name,
                player_index=self.index,
            )
        else:
            self.last_action = LastAction(description="problem")

        if card is not None and len(card.special_actions) > 0:
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
            description="dicarded_card",
            card=card.infos,
            player_name=self.name,
            player_index=self.index,
        )
        self._complete_action()

    def pass_turn(self):
        if not self.is_connected and not self.is_ai:
            self._number_turns_passed_not_connected += 1
            self.LOGGER.debug(
                f"Game n°{self.game_id}: player n°{self.id} ({self.name}) pass his/her turn "
                f"automatically (disconnected). "
                f"{self._number_turns_passed_not_connected}/"
                f"{self.MAX_NUMBER_TURN_EXPECTING_RECONNECT} before exclusion "
                f"from the game.",
            )

        self.last_action = LastAction(
            description="passed_turn", player_name=self.name, player_index=self.index
        )
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
        self._enable_passive_power()
        self._enable_trumps()

    def _enable_passive_power(self):
        if self._power.passive:
            self._power.create_effect(initiator=self, target=self, context={}).apply()

    def _enable_trumps(self):
        for trump_effect in self._trump_effects:
            trump_effect.apply()

    def complete_turn(self):
        self._revert_to_default()
        for trump in self._trump_effects:
            trump.consume()

        self._remove_consumed_trumps()

    def _remove_consumed_trumps(self):
        # If we modify the size of the size while looping on it, we will skip some element. For
        # instance if two elements are consumed in the list, only the first one will be removed.
        to_remove = []
        for trump in self._trump_effects:
            if trump.duration <= 0:
                to_remove.append(trump)

        for trump in to_remove:
            if trump in self._trump_effects:
                self._available_trumps = trump.teardown(self._available_trumps)
                self._trump_effects.remove(trump)

    def _revert_to_default(self):
        self._deck.revert_to_default()
        self._number_moves_to_play = self.MAX_NUMBER_MOVE_TO_PLAY

    def modify_number_moves(self, delta):
        self._number_moves_to_play += delta

    def modify_card_colors(self, colors, filter_=None):
        self._deck.modify_colors(colors, filter_=filter_)

    def modify_card_number_moves(self, delta, filter_=None):
        self._deck.modify_number_moves(delta, filter_=filter_)

    def set_special_actions_to_cards_in_deck(self, card_name, special_action_descriptions):
        self._deck.set_special_actions_to_card(card_name, special_action_descriptions)

    def modify_trump_effects_durations(self, delta, filter_=None):
        for trump in filter(filter_, self._trump_effects):
            trump.duration += delta

        self._remove_consumed_trumps()
        self._revert_to_default()
        self._enable_trumps()

    def play_special_action(self, action, target, context):
        target._check_for_cannot_be_affected_by_trumps(action)

        if target is not None:
            action.create_effect(initiator=self, target=target, context=context).apply()
            self._special_actions_names.remove(action.name.lower())
            self.last_action = LastAction(
                description="played_special_action",
                special_action=action,
                player_name=self.name,
                target_name=target.name,
                target_index=target.index,
                player_index=self.index,
            )

    def cancel_special_action(self, action):
        self._special_actions_names.remove(action.name.lower())

    def _affect_by(self, trump, *, initiator, context):
        self._check_can_be_affected_by_trump(trump)

        # The trump has just been played. We only trigger the effect if this is the target's turn.
        # If not, it will be applied once the turn begins.
        trump_played_infos = None
        trump_effect = trump.create_effect(target=self, initiator=initiator, context=context)
        # trump.affect may raise a TrumpHasNoEffect.
        # Only add the trump to the list if it had an effect.
        player_to_apply_trump_on = initiator if trump.apply_on_initiator else self
        if player_to_apply_trump_on._can_play:
            trump_effect.apply()
        player_to_apply_trump_on._trump_effects.append(trump_effect)

        # We must return the trump of the success infos to update the rest of the game.
        return trump_played_infos or trump

    def get_trump(self, trump_name, trump_color=None):
        if self._played_power_as_trump(trump_name, trump_color):
            return self.power
        return self._available_trumps[trump_name, trump_color]

    def _played_power_as_trump(self, trump_name, trump_color):
        return (
            self.power
            and not self.power.passive
            and trump_name == self.power.name
            and trump_color == self.power.color
        )

    def _check_can_be_affected_by_trump(self, trump):
        if len(self._trump_effects) >= self.MAX_NUMBER_AFFECTING_TRUMPS:
            raise imported_trumps.exceptions.MaxNumberAffectingTrumpsError

        if self._power and self._power.passive and not self._power.allow_trump_to_affect(trump):
            raise imported_trumps.exceptions.TrumpHasNoEffectError

        self._check_for_cannot_be_affected_by_trumps(trump)

    def _check_for_cannot_be_affected_by_trumps(self, trump):
        # A CannotBeAffectedByTrumps can be affecting the player, we need to check those too.
        for effect in self._trump_effects:
            if not effect.allow_trump_to_affect(trump) and trump.must_target_player:
                raise imported_trumps.exceptions.TrumpHasNoEffectError

    def play_trump(self, trump, *, target, context):
        self._check_play_trump(trump)

        try:
            trump_played_infos = target._affect_by(trump, initiator=self, context=context)
        except imported_trumps.exceptions.TrumpHasNoEffectError:
            self._end_play_trump(trump, target=target)
            raise
        else:
            self._end_play_trump(trump_played_infos, target=target)

    def _check_play_trump(self, trump):
        if not self.can_play:
            raise NotYourTurnError
        if self._number_trumps_played >= self.MAX_NUMBER_TRUMPS_PLAYED:
            raise imported_trumps.exceptions.MaxNumberTrumpPlayedError
        if not self._gauge.can_play_trump(trump):
            raise imported_trumps.exceptions.GaugeTooLowToPlayTrumpError

    def _end_play_trump(self, trump, *, target):
        self._number_trumps_played += 1
        self._gauge.play_trump(trump)
        self.last_action = LastAction(
            description="played_trump",
            trump=trump,
            player_name=self.name,
            target_name=getattr(target, "name", None),
            target_index=getattr(target, "index", None),
            player_index=self.index,
        )
        return trump

    def can_play_trump(self, trump):
        return (
            self.can_play
            and self._number_trumps_played < self.MAX_NUMBER_TRUMPS_PLAYED
            and self._gauge.can_play_trump(trump)
        )

    def __str__(self):  # pragma: no cover
        return "Player(id={id}, name={name}, index={index})".format(
            id=self.id, name=self.name, index=self.index
        )

    def __repr__(self):  # pragma: no cover
        return str(self)

    @property
    def on_last_line(self):
        return self._current_square in self._aim

    @property
    def _was_on_last_line_previous_move(self):
        return self._last_square_previous_turn in self._aim

    @property
    def trump_effects(self):
        return tuple(self._trump_effects)

    @property
    def ai_aim(self):
        return self.aim

    @property
    def aim(self):
        return self._aim

    @property
    def available_trumps(self) -> tuple:
        return tuple(self._available_trumps)

    @property
    def can_be_targeted_by_trumps(self):
        """Return true if the player can be targeted by at least one kind of trump.

        It returns false only when the player cannot be targeted by any trump.
        """
        for trump in self.trump_effects:
            if (
                isinstance(trump, imported_trumps.CannotBeAffectedByTrumps)
                and trump.is_affecting_all_trumps
            ):
                return False

        return True

    @property
    def can_play(self):
        return self._can_play

    @can_play.setter
    def can_play(self, value):
        self._can_play = bool(value)

    @property
    def can_power_be_played(self):
        return self.can_play_trump(self._power) if self._power else False

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
    def gauge(self):
        return self._gauge

    @property
    def hand(self):
        return self._deck.hand

    @property
    def hand_for_debug(self):
        return list(map(lambda card: "{} {}".format(card.name, card.color), self.hand))

    @property
    def has_remaining_moves_to_play(self):
        return self._number_moves_played < self._number_moves_to_play

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
    def on_aim_line(self):
        return self._current_square in self.aim

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
    def power(self):
        for effect in self._trump_effects:
            if stolen_power := effect.context.get("stolen_power"):
                return stolen_power

        return self._power

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
                "name": trump.name,
                "color": trump.color,
                "description": trump.description,
                "duration": trump.duration,
                "cost": trump.cost,
                "must_target_player": trump.must_target_player,
            }
            for trump in self._available_trumps
        ]

    @property
    def trumps_statuses(self):
        return [self.can_play_trump(trump) for trump in self._available_trumps]
