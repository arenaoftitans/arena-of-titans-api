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

import base64
import json
import logging
import uuid

from aot.config import config
from aot import get_game
from aot import get_number_players
from aot.game import Player
from aot.api.utils import (
    AotError,
    AotErrorToDisplay,
    RequestTypes,
)
from aot.api.ws import AotWs
from aot.utils import get_time
from contextlib import contextmanager


class Api(AotWs):
    # Class variables.
    INDEX_FIRST_PLAYER = 0
    AI_TIMEOUT = 6
    _error_messages = {
        'cannot_join': 'You cannot join this game. No slots opened.',
        'game_master_request': 'Only the game master can use {rt} request.',
        'inexistant_slot': 'Trying to update non existant slot.',
        'max_number_trumps': 'trumps.max_number_trumps',
        'max_number_played_trumps': 'trumps.max_number_played_trumps',
        'missing_trump_target': 'You must specify a target player.',
        'no_slot': 'No slot provided.',
        'not_your_turn': 'Not your turn.',
        'no_request': 'No request was provided',
        'registered_different_description': 'Number of registered players differs with number of '
                                            'players descriptions or too many/too few players are '
                                            'registered.',
        'unknown_error': 'Unknown error.',
        'unknown_request': 'Unknown request: {rt}.',
        'wrong_card': 'This card doesn\'t exist or is not in your hand.',
        'wrong_square': 'This square doesn\'t exist or you cannot move there yet.',
        'wrong_trump': 'Unknown trump.',
        'wrong_trump_target': 'Wrong target player index.',
    }

    # Instance variables
    _game_id = None
    _id = None
    _must_save_game = True
    _pending_ai = set()

    def onMessage(self, payload, isBinary):
        try:
            self._message = json.loads(payload.decode('utf-8'))
            self._rt = self._message.get('rt', '')
            if 'game_id' in self._message:
                self._game_id = self._message['game_id']
                self._cache.init(game_id=self._game_id, player_id=self.id)

            if self._rt not in RequestTypes:
                raise AotError('unknown_request', {'rt': self._rt})
            elif self._is_reconnecting:
                if self._can_reconnect:
                    self._reconnect()
                else:
                    raise AotErrorToDisplay('cannot_join')
            elif self._creating_new_game:
                self._create_new_game()
            elif self._creating_game:
                self._process_create_game_request()
            else:
                self._process_play_request()
        except AotErrorToDisplay as e:  # pragma: no cover
            self._send_error_to_display(str(e), e.infos)
        except AotError as e:
            self._send_error(str(e), e.infos)
        except Exception as e:  # pragma: no cover
            logging.exception('onMessage')

    def _create_new_game(self):
        self._game_id = base64.urlsafe_b64encode(uuid.uuid4().bytes)\
            .replace(b'=', b'')\
            .decode('ascii')
        self._initialize_cache(new_game=True)
        response = self._get_initialiazed_game_message(self.INDEX_FIRST_PLAYER)
        self.sendMessage(response)

    def _initialize_cache(self, new_game=False):
        self._cache.init(game_id=self._game_id, player_id=self._id)
        if new_game:
            self._cache.create_new_game(test=self._message.get('test', False))
        index = self._affect_current_slot()
        self._cache.save_session(index)
        return index

    def _get_initialiazed_game_message(self, index):  # pragma: no cover
        initiliazed_game = {
            'rt': RequestTypes.GAME_INITIALIZED,
            'is_game_master': False,
            'game_id': self._game_id,
            'player_id': self.id,
            'is_game_master': self._cache.is_game_master(),
            'index': index,
            'slots': self._cache.get_slots(include_player_id=False)
        }

        return initiliazed_game

    def _affect_current_slot(self):
        player_name = self._message.get('player_name', '')
        hero = self._message.get('hero', '')
        return self._cache.affect_next_slot(player_name, hero)

    def _process_create_game_request(self):
        if not self._current_request_allowed:
            raise AotErrorToDisplay('game_master_request', {'rt': self._rt})
        elif self._rt == RequestTypes.INIT_GAME:
            if self._can_join:
                self._join()
            else:
                raise AotErrorToDisplay('cannot_join')
        elif self._rt == RequestTypes.SLOT_UPDATED:
            self._modify_slots()
        elif self._rt == RequestTypes.CREATE_GAME:
            self._create_game()
        else:  # pragma: no cover
            raise AotError('unknown_error')

    def _join(self):
        index = self._initialize_cache()
        response = self._get_initialiazed_game_message(index)
        self.sendMessage(response)
        self._send_updated_slot_new_player(response['slots'][index])

    def _send_updated_slot_new_player(self, slot):
        message = {
            'rt': RequestTypes.SLOT_UPDATED,
            'slot': slot,
        }
        self._send_all_others(message)

    def _modify_slots(self):
        slot = self._message.get('slot', None)
        if slot is None:
            raise AotErrorToDisplay('no_slot')
        elif self._cache.slot_exists(slot):
            self._cache.update_slot(slot)
            # The player_id is stored in the cache so we can know to which player which slot is
            # associated. We don't pass this information to the frontend. If the slot is new, it
            # doesn't have a player_id yet, so we have to check for its existance before attempting
            # to delete it.
            if 'player_id' in slot:
                del slot['player_id']
            response = {
                'rt': RequestTypes.SLOT_UPDATED,
                'slot': slot
            }
            self._send_all(response)
        else:
            raise AotError('inexistant_slot')

    def _create_game(self):
        number_players = self._cache.number_taken_slots()
        create_game_request = self._message.get('create_game_request', None)
        if create_game_request is None:
            raise AotError('no_request')
        players_description = [player if player is not None and player.get('name', '') else None
                               for player in create_game_request]

        if not self._good_number_players_description(number_players, players_description) or\
                not self._good_number_player_registered(number_players):
            raise AotError('registered_different_description')

        self._initialize_game(players_description)
        self._cache.game_has_started()

    def _good_number_player_registered(self, number_players):
        return number_players >= 2 and number_players <= get_number_players()

    def _good_number_players_description(self, number_players, players_description):
        return number_players == len([player for player in players_description if player])

    def _initialize_game(self, players_description):
        slots = self._cache.get_slots()
        for player in players_description:
            if player:
                index = player['index']
                player['id'] = slots[index].get('player_id', None)
                player['is_ai'] = slots[index]['state'] == 'AI'

        game = get_game(players_description, test=self._cache.is_test())
        game.game_id = self._game_id
        game.is_debug = self._message.get('debug', False) and \
            config['api'].get('allow_debug', False)
        for player in game.players:
            if player is not None and player.id in self._clients:
                player.is_connected = True

        self._cache.save_game(game)
        self._send_game_created_message(game)

    def _send_game_created_message(self, game):  # pragma: no cover
        # Some session can be used for multiple players (mostly for debug purpose). We use the set
        # below to keep track of players' id and only send the first request for these sessions.
        # Otherwise, the list of cards for the first player to play would be overriden by the cards
        # of the last one.
        ids_message_sent = set()
        for player in game.players:
            if player is None or player.id in ids_message_sent:
                continue
            ids_message_sent.add(player.id)
            message = {
                'rt': RequestTypes.CREATE_GAME,
                'your_turn': game.active_player.id == player.id,
                'next_player': 0,
                'game_over': False,
                'winners': [],
                'players': [{
                    'index': player.index,
                    'name': player.name,
                    'hero': player.hero,
                } if player else None for player in game.players],
                'active_trumps': self._get_active_trumps_message(game),
                'hand': [{
                    'name': card.name,
                    'color': card.color,
                    'description': card.description,
                } for card in player.hand],
                'trumps': player.trumps
            }
            self._send_to(message, player.id)

    def _process_play_request(self):
        with self._load_game() as game:
            if self._is_player_id_correct(game):
                self._play_game(game)
                if game.active_player.is_ai:
                    self._play_ai_after_timeout()
            elif game.active_player.is_ai:
                self._play_ai(game)
            else:
                self._must_save_game = False
                raise AotErrorToDisplay('not_your_turn')

    def _play_ai_after_timeout(self):
        logging.debug('Game n°{game_id}: schedule play for AI'.format(game_id=self._game_id))
        self._pending_ai.add(self._game_id)
        self._loop.call_later(self.AI_TIMEOUT, self._process_play_request)

    def _play_ai(self, game):
        self._pending_ai.discard(self._game_id)
        if game.active_player.is_ai:
            this_player = game.active_player
            if game.is_debug:
                self._send_debug({
                    'player': this_player.name,
                    'hand': this_player.hand_for_debug,
                })
            game.play_auto()
            self._send_play_message(game, this_player)
            if game.active_player.is_ai:
                self._play_ai_after_timeout()

    @contextmanager
    def _load_game(self):
        self._must_save_game = True
        game = self._get_game()
        self._disconnect_pending_players(game)
        self._reconnect_pending_players(game)

        yield game

        if self._must_save_game:
            self._save_game(game)

    def _disconnect_pending_players(self, game):
        self._change_players_connection_status(
            game,
            self._clients_pending_disconnection_for_game,
            False,
        )

    def _change_players_connection_status(self, game, player_ids, status):
        while len(player_ids) > 0:
            player_id = player_ids.pop()
            player = game.get_player_by_id(player_id)
            player.is_connected = status

    def _reconnect_pending_players(self, game):
        self._change_players_connection_status(
            game,
            self._clients_pending_reconnection_for_game,
            True,
        )

    def _get_game(self):
        return self._cache.get_game()

    def _save_game(self, game):
        self._cache.save_game(game)

    def _is_player_id_correct(self, game):
        return self.id is not None and self.id == game.active_player.id

    def _play_game(self, game):
        play_request = self._message.get('play_request', None)
        if play_request is None:
            raise AotError('no_request')
        elif self._rt == RequestTypes.VIEW_POSSIBLE_SQUARES:
            self._view_possible_squares(game, play_request)
        elif self._rt == RequestTypes.PLAY:
            self._play(game, play_request)
        elif self._rt == RequestTypes.PLAY_TRUMP:
            self._play_trump(game, play_request)
        else:
            raise AotError('unknown_request', {'rt': self._rt})

    def _view_possible_squares(self, game, play_request):
        card = self._get_card(game, play_request)
        if card is not None:
            possible_squares = game.view_possible_squares(card)
            self.sendMessage({
                'rt': RequestTypes.VIEW_POSSIBLE_SQUARES,
                'possible_squares': possible_squares
            })
        else:
            raise AotErrorToDisplay('wrong_card')

    def _get_card(self, game, play_request):
        name = play_request.get('card_name', None)
        color = play_request.get('card_color', None)
        return game.active_player.get_card(name, color)

    def _play(self, game, play_request):
        this_player = game.active_player
        if play_request.get('pass', False):
            game.pass_turn()
        elif play_request.get('discard', False):
            card = self._get_card(game, play_request)
            if card is None:
                raise AotErrorToDisplay('wrong_card')
            game.discard(card)
        else:
            card = self._get_card(game, play_request)
            square = self._get_square(play_request, game)
            if card is None:
                raise AotErrorToDisplay('wrong_card')
            elif square is None or not game.can_move(card, square):
                raise AotErrorToDisplay('wrong_square')
            game.play_card(card, square)

        self._send_play_message(game, this_player)

    def _get_square(self, play_request, game):
        x = play_request.get('x', None)
        y = play_request.get('y', None)
        return game.get_square(x, y)

    def _send_play_message(self, game, this_player):  # pragma: no cover
        game.add_action(this_player.last_action)
        self._send_player_played_message(this_player, game)

        for player in game.players:
            if player is not None and player.id in self._clients:
                self._clients[player.id].sendMessage(self._get_play_message(player, game))

    def _send_player_played_message(self, player, game):  # pragma: no cover
        self._send_all({
            'rt': RequestTypes.PLAYER_PLAYED,
            'player_index': player.index,
            'new_square': {
                'x': player.current_square.x,
                'y': player.current_square.y,
            },
            'last_action': self._get_action_message(player.last_action),
            'game_over': game.is_over,
            'winners': game.winners,
        })

    def _get_action_message(self, action):  # pragma: no cover
        if action is not None:
            return {
                'description': action.description,
                'card': action.card,
                'trump': action.trump,
                'player_name': action.player_name,
                'target_name': action.target_name,
                'player_index': action.player_index,
            }

    def _get_play_message(self, player, game):
        return {
            'rt': RequestTypes.PLAY,
            'your_turn': player.id == game.active_player.id,
            'on_last_line': player.on_last_line,
            'has_won': player.has_won,
            'rank': player.rank,
            'next_player': game.active_player.index,
            'hand': [{
                'name': card.name,
                'color': card.color,
                'description': card.description,
            } for card in player.hand],
            'active_trumps': self._get_active_trumps_message(game),
            'elapsed_time': get_time() - game.active_player.turn_start_time,
        }

    def _get_active_trumps_message(self, game):
        return [{
                'player_index': game_player.index,
                'player_name': game_player.name,
                'trumps': game_player.affecting_trumps
                } if game_player else None for game_player in game.players]

    def _play_trump(self, game, play_request):
        trump = self._get_trump(game, play_request.get('name', ''))
        targeted_player_index = play_request.get('target_index', None)
        if trump is None:
            raise AotError('wrong_trump')
        elif trump.must_target_player and targeted_player_index is None:
            raise AotError('missing_trump_target')

        if trump.must_target_player:
            trump.initiator = game.active_player.name
            self._play_trump_with_target(game, trump, targeted_player_index)
        else:
            self._play_trump_without_target(game, trump)

    def _play_trump_with_target(self, game, trump, targeted_player_index):
        if targeted_player_index < len(game.players):
            target = game.players[targeted_player_index]
            if target and game.active_player.play_trump(trump, target=target):
                last_action = game.active_player.last_action
                game.add_action(last_action)
                message = {
                    'rt': RequestTypes.PLAY_TRUMP,
                    'active_trumps': self._get_active_trumps_message(game),
                    'last_action': self._get_action_message(last_action),
                }
                self._send_all(message)
            else:
                self._send_trump_error(game.active_player)
        else:
            raise AotError('wrong_trump_target')

    def _send_trump_error(self, active_player):
        if not active_player.can_play_trump:
            raise AotErrorToDisplay(
                'max_number_played_trumps',
                {'num': Player.MAX_NUMBER_TRUMPS_PLAYED},
            )
        else:
            raise AotErrorToDisplay(
                'max_number_trumps',
                {'num': Player.MAX_NUMBER_AFFECTING_TRUMPS},
            )

    def _play_trump_without_target(self, game, trump):
        self._play_trump_with_target(game, trump, game.active_player.index)

    def _get_trump(self, game, play_request):
        return game.active_player.get_trump(play_request.title())

    @property
    def _can_join(self):
        return self._cache.game_exists(self._game_id) and \
            self._cache.has_opened_slots(self._game_id)

    @property
    def _creating_game(self):
        return not self._cache.has_game_started()

    @property
    def _creating_new_game(self):
        return self._game_id is None or \
            (self._rt == RequestTypes.INIT_GAME and 'game_id' not in self._message)

    @property
    def _current_request_allowed(self):
        return self._cache.is_game_master() or \
                self._rt in (RequestTypes.SLOT_UPDATED, RequestTypes.INIT_GAME)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
