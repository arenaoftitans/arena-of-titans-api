from autobahn.asyncio.websocket import WebSocketServerProtocol
import asyncio
import base64
import copy
import json
import uuid

from aot import get_game
from aot import get_number_players
from aot.game import Player
from aot.api.api_cache import ApiCache
from aot.api.utils import to_json
from aot.api.utils import RequestTypes


class Api(WebSocketServerProtocol):
    # Class variables.
    _clients = {}
    _error_messages = {
        'add_slot_exists': 'Trying to add a slot that already exists.',
        'cannot_join': 'You cannot join this game. No slots opened.',
        'game_master_request': 'Only the game master can use {rt} request.',
        'inexistant_slot': 'Trying to update non existant slot.',
        'max_number_slots_reached': 'Max number of slots reached. You cannot add more slots.',
        'max_number_trumps': 'A player cannot be affected by more than {num} trump(s).',
        'max_number_played_trumps': 'You can only play {num} trump(s) per turn',
        'missing_trump_target': 'You must specify a target player.',
        'no_slot': 'No slot provided.',
        'not_enought_players': 'Not enough player to create game. 2 Players are at least required '
                               'to start a game.',
        'not_your_turn': 'Not your turn.',
        'registered_different_description': 'Number of registered players differs with number of '
                                            'players descriptions.',
        'unknown_error': 'Unknown error.',
        'unknown_request': 'Unknown request: {rt}.',
        'wrong_card': 'This card doesn\'t exist or is not in your hand.',
        'wrong_square': 'This square doesn\'t exist or you cannot move there yet.',
        'wrong_trump': 'Unknown trump.',
        'wrong_trump_target': 'Wrong target player index.',
    }

    # Instance variables
    _game_id = None
    _cache = None
    _id = None
    _message = None
    _loop = None

    def sendMessage(self, message):
        if isinstance(message, dict):
            message = json.dumps(message, default=to_json)
        message = message.encode('utf-8')
        if isinstance(message, bytes):
            super().sendMessage(message)

    def onOpen(self):
        self.id = self._wskey
        Api._clients[self.id] = self
        self._loop = asyncio.get_event_loop()
        self._set_up_connection_keep_alive()

    def _set_up_connection_keep_alive(self):
        self._loop.call_later(5, self.sendPing)

    def onPong(self, payload):
        self._set_up_connection_keep_alive()

    def onMessage(self, payload, isBinary):
        self.message = json.loads(payload.decode('utf-8'))
        if self._game_id is None:
            if not self._initialize_connection():
                self.sendClose()
        elif self._creating_game():
            self._process_create_game_request()
        else:
            self._process_play_request()

    def _initialize_connection(self):
        must_close_session = False
        if self.message['rt'] == RequestTypes.INIT_GAME.value and 'game_id' in self.message:
            self._game_id = self.message['game_id']
        else:
            self._game_id = base64.urlsafe_b64encode(uuid.uuid4().bytes)\
                .replace(b'=', b'')\
                .decode('ascii')

        if self._can_join() and not self._is_reconnecting():
            response = self._initialize_cache()
        elif self._is_reconnecting() and self._can_reconnect():
            response = self._reconnect()
        else:
            must_close_session = True
            response = self._format_error_to_display('cannot_join')

        self.sendMessage(response)

        return not must_close_session

    def _can_join(self):
        return ApiCache.is_new_game(self._game_id) or \
            (ApiCache.game_exists(self._game_id) and ApiCache.has_opened_slots(self._game_id))

    def _initialize_cache(self):
        self._cache = ApiCache(self._game_id, self.id)
        if ApiCache.is_new_game(self._game_id):
            self._cache.create_new_game()

        index = self._affect_current_slot()
        self._cache.save_session(index)

        initiliazed_game = self._get_initialiazed_game_message(index)
        self._send_updated_slot_new_player(
            initiliazed_game['slots'][index],
            initiliazed_game['is_game_master'])
        return initiliazed_game

    def _get_initialiazed_game_message(self, index):
        initiliazed_game = {
            'rt': RequestTypes.GAME_INITIALIZED.value,
            'is_game_master': False,
            'game_id': self._game_id,
            'player_id': self.id,
            'is_game_master': self._cache.is_game_master(),
            'index': index,
            'slots': self._cache.get_slots(include_player_id=False)
        }

        return initiliazed_game

    def _affect_current_slot(self):
        return self._cache.affect_next_slot(self.message.get('player_name', ''))

    def _send_updated_slot_new_player(self, slot, is_game_master):
        # The game master is the first player, no other players to send to
        if not is_game_master:
            updated_slot = copy.deepcopy(slot)
            message = {
                'rt': RequestTypes.SLOT_UPDATED.value,
                'slot': updated_slot
            }
            self._send_all_others(message)

    def _is_reconnecting(self):
        return 'player_id' in self.message

    def _can_reconnect(self):
        return ApiCache.is_member_game(self._game_id, self.message['player_id'])

    def _reconnect(self):
        self.id = self.message['player_id']
        self._clients[self.id] = self
        self._cache = ApiCache(self._game_id, self.id)
        if self._creating_game():
            index = self._cache.get_player_index()
            return self._get_initialiazed_game_message(index)
        else:
            game = self._load_game()
            player = [player for player in game.players if player.id == self.id][0]
            message = self._get_play_message(player, game)
            message['reconnect'] = [{
                'index': player.index,
                'square': player.current_square
            } for player in game.players]
            return message

    def _creating_game(self):
        return not self._cache.has_game_started()

    def _process_create_game_request(self):
        if not self._cache.is_game_master() and \
                self.message['rt'] != RequestTypes.SLOT_UPDATED.value:
            rt = self.message['rt']
            self._send_error_to_display('game_master_request', {'rt': rt})
        else:
            self._do_create_game_request()

    def _do_create_game_request(self):
        rt = self.message['rt']
        if rt not in RequestTypes.__members__:
            self._send_error('unknown_request', {'rt': rt})
        if rt in (RequestTypes.ADD_SLOT.value, RequestTypes.SLOT_UPDATED.value):
            self._modify_slots(rt)
        elif rt == RequestTypes.CREATE_GAME.value:
            number_players = self._cache.number_taken_slots()
            players_description = [player for player in self.message['create_game_request']
                                   if player['name']]
            if self._good_number_player_registered(number_players) and \
                    self._good_number_players_description(number_players, players_description):
                self._initialize_game(players_description)
            elif not self._good_number_players_description(number_players, players_description):
                self._send_error('registered_different_description')
            elif number_players < 2 or len(players_description) < 2:
                self._send_error_to_display('not_enought_players')
        else:
            self._send_error_to_display('unknown_error')

    def _modify_slots(self, rt):
        slot = self.message.get('slot', None)
        if slot is None:
            self._send_error_to_display('no_slot')
            return
        elif rt == RequestTypes.ADD_SLOT.value:
            if not self._max_number_slots_reached() and not self._cache.slot_exists(slot):
                self._cache.add_slot(slot)
            elif self._cache.slot_exists(slot):
                self._send_error_to_display('add_slot_exists')
            else:
                self._send_error_to_display('max_number_slots_reached')
                return
        elif self._cache.slot_exists(slot):
            self._cache.update_slot(slot)
        else:
            self._send_error_to_display('inexistant_slot')
            return
        # The player_id is stored in the cache so we can know to which player which slot is
        # associated. We don't pass this information to the frontend. If the slot is new, it
        # doesn't have a player_id yet
        if 'player_id' in slot:
            del slot['player_id']
        response = {
            'rt': RequestTypes.SLOT_UPDATED.value,
            'slot': slot
        }
        self._send_all(response)

    def _max_number_slots_reached(self):
        return len(self._cache.get_slots()) == get_number_players()

    def _good_number_player_registered(self, number_players):
        return number_players >= 2 and number_players <= get_number_players()

    def _good_number_players_description(self, number_players, players_description):
        return number_players == len(players_description)

    def _initialize_game(self, players_description):
        self._create_game(players_description)
        self._cache.game_has_started()

    def _create_game(self, players_description):
        slots = self._cache.get_slots()
        for player in players_description:
            index = player['index']
            player['id'] = slots[index]['player_id']

        game = get_game(players_description)
        self._cache.save_game(game)
        self._send_game_created_message(game)

    def _send_game_created_message(self, game):
        # Some session can be used for multiple players (mostly for debug purpose). We use the set
        # below to keep track of players' id and only send the first request for these sessions.
        # Otherwise, the list of cards for the first player to play would be overriden by the cards
        # of the last one.
        ids_message_sent = set()
        for player in game.players:
            if player.id in ids_message_sent:
                continue
            ids_message_sent.add(player.id)
            message = {
                'rt': RequestTypes.CREATE_GAME.value,
                'your_turn': game.active_player.id == player.id,
                'next_player': 0,
                'game_over': False,
                'winners': [],
                'players': [{
                    'index': player.index,
                    'name': player.name
                } for player in game.players],
                'active_trumps': [{
                    'player_index': player.index,
                    'player_name': player.name,
                    'trumps_names': [trump.name for trump in player.affecting_trumps]
                } for player in game.players],
                'hand': [{
                    'name': card.name,
                    'color': card.color
                } for card in player.hand],
                'trumps': player.trumps
            }
            self._send_to(message, player.id)

    def _process_play_request(self):
        game = self._load_game()
        if self._is_player_id_correct(game):
            self._play_game(game)
            self._save_game(game)
        else:
            self._send_error_to_display('not_your_turn')

    def _load_game(self):
        return self._cache.get_game()

    def _is_player_id_correct(self, game):
        return self.id is not None and self.id == game.active_player.id

    def _play_game(self, game):
        rt = self.message['rt']
        play_request = self.message.get('play_request', {})
        if rt == RequestTypes.VIEW_POSSIBLE_SQUARES.value:
            self._view_possible_squares(game, play_request)
        elif rt == RequestTypes.PLAY.value:
            self._play_card(game, play_request)
        elif rt == RequestTypes.PLAY_TRUMP.value:
            self._play_trump(game, play_request)
        else:
            return self._send_error('unknown_request', {'rt': rt})

    def _view_possible_squares(self, game, play_request):
        card = self._get_card(play_request, game)
        if card is not None:
            possible_squares = game.view_possible_squares(card)
            self.sendMessage({
                'rt': RequestTypes.VIEW_POSSIBLE_SQUARES.value,
                'possible_squares': possible_squares
            })
        else:
            self._send_error_to_display('wrong_card')

    def _get_card(self, play_request, game):
        name = play_request.get('card_name', None)
        color = play_request.get('card_color', None)
        return game.active_player.get_card(name, color)

    def _play_card(self, game, play_request):
        this_player = game.active_player
        error = False
        if play_request.get('pass', False):
            game.pass_turn()
        elif play_request.get('discard', False):
            card = self._get_card(play_request, game)
            game.discard(card)
        else:
            card = self._get_card(play_request, game)
            square = self._get_square(play_request, game)
            if card is not None and square is not None and game.can_move(card, square):
                game.play_card(card, square)
            elif card is None:
                error = True
                self._send_error_to_display('wrong_card')
            elif square is None or not game.can_move(card, square):
                error = True
                self._send_error_to_display('wrong_square')

        if not error:
            self._send_play_message(this_player, game)

    def _get_square(self, play_request, game):
        x = play_request.get('x', None)
        y = play_request.get('y', None)
        return game.get_square(x, y)

    def _send_play_message(self, this_player, game):
        # Send play message to the player who just played.
        active_player_id = game.active_player.id
        active_player_index = game.active_player.index
        self._send_player_moved_message(this_player)
        this_player_message = self._get_play_message(this_player, game)
        self._clients[self.id].sendMessage(this_player_message)

        # Send to the next player if it is not the player who just played.
        if this_player.index != active_player_index and active_player_id in self._clients:
            active_player_message = self._get_play_message(game.active_player, game)
            active_player_message['your_turn'] = True
            self._clients[active_player_id].sendMessage(active_player_message)

    def _send_player_moved_message(self, player):
        self._send_all({
            'rt': RequestTypes.PLAYER_MOVED.value,
            'player_index': player.index,
            'new_square': {
                'x': player.current_square.x,
                'y': player.current_square.y,
            }
        })

    def _get_play_message(self, player, game):
        return {
            'rt': RequestTypes.PLAY,
            'your_turn': player.id == game.active_player.id,
            'next_player': game.active_player.index,
            'hand': [{
                'name': card.name,
                'color': card.color
            } for card in player.hand],
            'game_over': game.is_over,
            'winners': game.winners,
            'active_trumps': self._get_trump_message(game)
        }

    def _get_trump_message(self, game):
        return [{
                'player_index': game_player.index,
                'player_name': game_player.name,
                'trumps_names': [trump.name for trump in game_player.affecting_trumps]
                } for game_player in game.players]

    def _play_trump(self, game, play_request):
        trump = self._get_trump(game, play_request.get('name', ''))
        targeted_player_index = play_request.get('target_index', None)
        if trump is None:
            self._send_error_to_display('wrong_trump')
        elif trump.must_target_player and targeted_player_index is None:
            self._send_error('missing_trump_target')
        elif trump.must_target_player:
            self._play_trump_with_target(game, trump, targeted_player_index)
        else:
            self._play_trump_without_target(game, trump)

    def _play_trump_with_target(self, game, trump, targeted_player_index):
        if targeted_player_index < len(game.players):
            target = game.players[targeted_player_index]
            if game.active_player.play_trump(trump, target=target):
                message = {
                    'rt': RequestTypes.PLAY_TRUMP.value,
                    'active_trumps': self._get_trump_message(game)
                }
                self._send_all(message)
            else:
                self._send_trump_error(game.active_player)
        else:
            self._send_error_to_display('wrong_trump_target')

    def _send_trump_error(self, active_player):
        if not active_player.can_play_trump:
            self._send_error_to_display(
                'max_number_played_trumps',
                format_opt={'num': Player.MAX_NUMBER_TRUMPS_PLAYED})
        else:
            self._send_error_to_display(
                'max_number_trumps',
                format_opt={'num': Player.MAX_NUMBER_AFFECTING_TRUMPS})

    def _play_trump_without_target(self, game, trump):
        self._play_trump_with_target(game, trump, game.active_player.index)

    def _get_trump(self, game, play_request):
        return game.active_player.get_trump(play_request.title())

    def _save_game(self, game):
        self._cache.save_game(game)

    def onClose(self, wasClean, code, reason):
        if self.id in self._clients:
            del self._clients[self.id]

    def _send_all(self, message, excluded_players=set()):
        for player_id in self._cache.get_players_ids():
            player = self._clients.get(player_id, None)
            if player is not None and player_id not in excluded_players:
                player.sendMessage(message)

    def _send_all_others(self, message):
        self._send_all(message, excluded_players=set([self.id]))

    def _send_to(self, message, id):
        if id in self._clients:
            self._clients[id].sendMessage(message)

    def _format_error_to_display(self, message, format_opt={}):
        return {'error_to_display': self._get_error(message, format_opt)}

    def _get_error(self, message, format_opt):
        return self._error_messages.get(message, message).format(**format_opt)

    def _send_error(self, message, format_opt={}):
        self.sendMessage(self._format_error(message, format_opt))

    def _send_error_to_display(self, message, format_opt={}):
        self.sendMessage(self._format_error_to_display(message, format_opt))

    def _send_all_error(self, message, format_opt={}):
        self._send_all(self._format_error(message, format_opt))

    def _format_error(self, message, format_opt={}):
        return {'error': self._get_error(message, format_opt)}

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
