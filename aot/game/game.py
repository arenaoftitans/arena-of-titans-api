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

import daiquiri

from .ai import (
    find_cheapest_card,
    find_move_to_play,
)
from ..cards.trumps.exceptions import NonExistantTrumpTarget


class Game:
    LOGGER = daiquiri.getLogger(__name__)

    _actions = None
    _active_player = None
    _board = None
    _game_id = None
    _index_first_player = 0
    _is_debug = False
    _is_over = False
    _nb_turns = 0
    _next_rank_available = 1
    _players = []
    _players_id_to_index = None
    _winners = []

    def __init__(self, board, players):
        self._actions = []
        self._active_player = players[0]
        self._index_first_player = self._active_player.index
        self._board = board
        self._is_over = False
        self._players = players
        self._players_id_to_index = {player.id: index for index, player in enumerate(players)
                                     if player}
        self._nb_turns = 0
        self._next_rank_available = 1
        self._winners = []

        self._active_player.init_turn()

    def add_action(self, action):
        self._actions.append(action)

    def get_player_by_id(self, player_id):
        player_index = self._players_id_to_index[player_id]
        player = self._players[player_index]

        return player

    def view_possible_squares(self, card):
        return self._active_player.view_possible_squares(card)

    def play_card(self, card, square, check_move=True):
        has_special_actions = self._active_player.play_card(card, square, check_move=check_move)
        if not has_special_actions:
            self._continue_game_if_enough_players()

        return has_special_actions

    def play_trump(self, trump, *, target_index):
        try:
            target = self.players[target_index]
        except IndexError:
            raise NonExistantTrumpTarget
        else:
            self.active_player.play_trump(trump, target=target)

    def play_special_action(self, action, target=None, action_args=None):
        self.active_player.play_special_action(action, target=target, action_args=action_args)

    def cancel_special_action(self, action):
        self.active_player.cancel_special_action(action)

    def complete_special_actions(self):
        self.active_player.complete_special_actions()
        self._continue_game_if_enough_players()

    def can_move(self, card, square):
        return self._active_player.can_move(card, square)

    def get_square(self, x, y):
        return self._board[x, y]

    def _continue_game_if_enough_players(self):
        while not self._is_over:
            if self._has_enough_players_to_continue():
                self._active_player = self._find_next_player()
                if self._active_player.is_connected or self._active_player.is_ai:
                    break
                else:
                    self._active_player.pass_turn()
            else:
                self._is_over = True

    def _has_enough_players_to_continue(self):
        remaining_ai = set()
        remaining_human_players = set()
        for player in self._players:
            if player is not None and player.still_in_game:
                if player.is_ai:
                    remaining_ai.add(player)
                else:
                    remaining_human_players.add(player)
            elif player is not None and not player.is_ai:
                self.LOGGER.debug(
                    f'Game n°{self.game_id}: player n°{player.id} ({player.name}) has '
                    f'been disconnected too long. Remove from remaining players',
                )
        remaining_players = remaining_ai.union(remaining_human_players)

        if len(remaining_human_players) == 1 and len(remaining_ai) == 0:
            last_player = remaining_human_players.pop()
            if last_player.is_connected:
                self._add_to_winners(last_player)

        return len(remaining_players) > 1 and len(remaining_human_players) >= 1

    def _find_next_player(self):
        if self._active_player.can_play:
            return self._active_player
        else:
            self._active_player.complete_turn()
            return self._get_next_player()

    def _get_next_player(self):
        while True:
            next_player = self._get_next_player_in_list()
            next_player.init_turn()

            if next_player.has_reached_aim:
                self._add_to_winners(next_player)
            if not next_player.has_won or self._is_over:
                break
        return next_player

    def _get_next_player_in_list(self):
        index_next_player = self._get_index_next_player(self._active_player.index)
        if index_next_player == len(self._players):
            index_next_player = self._get_index_next_player(0, is_start_index=True)

        return self._players[index_next_player]

    def _get_index_next_player(self, current_index, is_start_index=False):
        if not is_start_index:
            index_next_player = current_index + 1
        else:
            index_next_player = current_index

        while index_next_player < len(self._players):
            player = self._players[index_next_player]
            if player is not None and player.index == self._index_first_player:
                self._nb_turns += 1
            if player is not None and not player.has_won:
                break
            index_next_player += 1

        return index_next_player

    def _add_to_winners(self, winner):
        winner.wins(rank=self._next_rank_available)
        self._next_rank_available += 1
        self._winners.append(winner)
        if not self._has_enough_players_to_continue():
            self._is_over = True
            # If we are here, there is only one or zero player left. If the
            # last remaining players. won during the same turn, there is no
            # more player who has not won. This is the easiest the remainding
            # player.
            self._winners.extend([player for player in self._players
                                  if player is not None and not player.has_won])

    def pass_turn(self):
        self._active_player.pass_turn()
        self._continue_game_if_enough_players()

    def discard(self, card):
        self._active_player.discard(card)
        self._continue_game_if_enough_players()

    def play_auto(self):
        if self.active_player.on_last_line or not self.active_player.has_remaining_moves_to_play:
            self.pass_turn()
            return

        card, square = find_move_to_play(
            self.active_player.hand,
            self.active_player.current_square,
            self.active_player.ai_aim,
            self._board,
        )
        if card:
            self.play_card(card, square)
            if card.special_actions:
                self.complete_special_actions()
        else:
            cheapest_card = find_cheapest_card(self.active_player.hand)
            self.discard(cheapest_card)

    def __eq__(self, other):
        if not isinstance(other, Game):
            return False
        # If game_id is not set, we can't know whether the instance are equal.
        elif other.game_id is None or self.game_id is None:
            return False

        return self is other or self.game_id == other.game_id

    @property
    def active_player(self):
        return self._active_player

    @property
    def game_id(self):  # pragma: no cover
        return self._game_id

    @game_id.setter
    def game_id(self, value):
        if self._game_id is not None:  # pragma: no cover
            self.LOGGER.warn(
                f'Changing game id for game {self._game_id} to {value}',
            )
        self._game_id = value
        for player in self.players:
            if player:
                player.game_id = value

    @property
    def is_debug(self):
        return self._is_debug

    @is_debug.setter
    def is_debug(self, value):
        self._is_debug = bool(value)

    @property
    def is_over(self):
        return self._is_over

    @property
    def last_action(self):
        if len(self._actions) == 0:
            return None
        else:
            return self._actions[-1]

    @property
    def nb_turns(self):
        return self._nb_turns

    @property
    def players(self):
        return self._players

    @property
    def winners(self):
        return [player.name for player in self._winners]
