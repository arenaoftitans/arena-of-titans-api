from autobahn.asyncio.websocket import WebSocketServerProtocol
import base64
import copy
import json
import uuid

from aot import get_game
from aot import get_number_players
from aot.api.api_cache import ApiCache
from aot.api.utils import to_json
from aot.api.utils import RequestTypes


class Api(WebSocketServerProtocol):
    # Class variables.
    _clients = {}
    _cache = ApiCache()

    # Instance variables
    _game_id = None
    _id = None
    _message = None

    def sendMessage(self, message):
        if isinstance(message, str):
            message = message.encode('utf-8')
        else:
            message = json.dumps(message, default=to_json).encode('utf-8')
        if isinstance(message, bytes):
            super().sendMessage(message)

    def onOpen(self):
        self.id = self._wskey
        Api._clients[self.id] = self

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
        if self._can_join():
            response = self._initialize_cache()
            self.sendMessage(response)
        else:
            must_close_session = True
            response = self._format_error_to_display(
                'You cannot join this game. No slots opened.')
        self.sendMessage(response)

        return not must_close_session

    def _can_join(self):
        return self._cache.is_new_game(self._game_id) or \
            (self._cache.game_exists(self._game_id) and self._cache.has_opened_slots(self._game_id))

    def _initialize_cache(self):
        initiliazed_game = {
            'rt': RequestTypes.GAME_INITIALIZED.value,
            'is_game_master': False,
            'game_id': self._game_id
        }
        if self._cache.is_new_game(self._game_id):
            self._cache.init(self._game_id, self.id)
            initiliazed_game['is_game_master'] = True

        index = self._affect_current_slot()
        self._cache.save_session(self._game_id, self.id, index)
        initiliazed_game['index'] = index
        initiliazed_game['slots'] = self._cache.get_slots(self._game_id, include_player_id=False)
        self._send_updated_slot_new_player(
            initiliazed_game['slots'][index],
            initiliazed_game['is_game_master'])
        return initiliazed_game

    def _affect_current_slot(self):
        return self._cache.affect_next_slot(self._game_id, self.id, self.message.get('player_name', ''))

    def _send_updated_slot_new_player(self, slot, is_game_master):
        # The game master is the first player, no other players to send to
        if not is_game_master:
            updated_slot = copy.deepcopy(slot)
            updated_slot['rt'] = RequestTypes.SLOT_UPDATED.value
            self._send_all_others(updated_slot)

    def _creating_game(self):
        return not self._cache.has_game_started(self._game_id)

    def _process_create_game_request(self):
        if not self._cache.is_game_master(self._game_id, self.id) and \
                self.message['rt'] != RequestTypes.SLOT_UPDATED.value:
            self._send_error_to_display('Only the game master can create the game.')
        else:
            self._do_create_game_request()

    def _do_create_game_request(self):
        rt = self.message['rt']
        if rt not in RequestTypes.__members__:
            self._send_all_error('Unknown request.')
        if rt in (RequestTypes.ADD_SLOT.value, RequestTypes.SLOT_UPDATED.value):
            self._modify_slots(rt)
        elif rt == RequestTypes.CREATE_GAME.value:
            number_players = self._cache.number_taken_slots(self._game_id)
            players_description = [player for player in self.message['create_game_request'] if player['name']]
            if self._good_number_player_registered(number_players) and \
                    self._good_number_players_description(number_players, players_description):
                self._send_all(self._initialize_game(players_description))
            elif not self._good_number_players_description(number_players, players_description):
                self._send_error('Number of registered players differs with number of players descriptions.')
            elif number_players < 2 or len(players_description) < 2:
                self._send_error_to_display('Not enough player to create game. 2 Players are at least required to start a game.')
        else:
            self._send_error_to_display('Unknown error.')

    def _modify_slots(self, rt):
        slot = self.message['slot']
        import logging
        logging.debug('**************')
        logging.debug(rt)
        logging.debug(slot)
        logging.debug(rt == RequestTypes.ADD_SLOT.value)
        if rt == RequestTypes.ADD_SLOT.value:
            if not self._max_number_slots_reached():
                self._cache.add_slot(self._game_id, slot)
            else:
                self._send_error_to_display('Max number of slots reached. You cannot add more slots.')
                return
        else:
            self._cache.update_slot(self._game_id, self.id, slot)
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
        return len(self._cache.get_slots(self._game_id)) == get_number_players()

    def _good_number_player_registered(self, number_players):
        return number_players >= 2 and number_players <= get_number_players()

    def _good_number_players_description(self, number_players, players_description):
        return number_players == len(players_description)

    def _initialize_game(self, players_description):
        self._create_game(players_description)
        self._cache.game_has_started(self._game_id)

    def _create_game(self, players_description):
        players_ids = self._cache.get_players_ids(self._game_id)
        for player in players_description:
            index = player['index']
            player['id'] = players_ids[index]

        game = get_game(players_description)
        self._cache.save_game(game, self._game_id)
        self._send_game_created_message(game)

    def _send_game_created_message(self, game):
        for player in game.players:
            message = {
                'rt': RequestTypes.CREATE_GAME.value,
                'your_turn': game.active_player.id == player.id,
                'next_player': {
                    'index': 0,
                    'name': game.players[0].name
                },
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
            self._send_error_to_display('Not your turn.')

    def _load_game(self):
        return self._cache.get_game(self._game_id)

    def _is_player_id_correct(self, game):
        return self.id is not None and self.id == game.active_player.id

    def _play_game(self, game):
        rt = self.message['rt']
        play_request = self.message.get('play_request', {})
        if rt == RequestTypes.VIEW_POSSIBLE_SQUARES.value:
            self._view_possible_squares(game, play_request)
        if rt == RequestTypes.PLAY.value:
            self._play_card(game, play_request)

    def _view_possible_squares(self, game, play_request):
        card = self._get_card(play_request, game)
        if card is not None:
            possible_squares = game.view_possible_squares(card)
            self.sendMessage({
                'rt': RequestTypes.VIEW_POSSIBLE_SQUARES.value,
                'possible_squares': possible_squares
            })
        else:
            self._send_error_to_display('This card doesn\'t exist or is not in your hand.')

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
                self._send_error_to_display('This card doesn\'t exist or is not in your hand.')
            elif square is None or not game.can_move(card, square):
                error = True
                self._send_error_to_display('This square doesn\'t exist or you cannot move there yet.')

        if not error:
            self._send_play_message(this_player, game)

    def _get_square(self, play_request, game):
        x = play_request.get('x', None)
        y = play_request.get('y', None)
        return game.get_square(x, y)

    def _send_play_message(self, this_player, game):
        # Send play message to the player who just played.
        active_player_id = game.active_player.id
        this_player_message = self._get_play_message(this_player, game)
        self._clients[self.id].sendMessage(this_player_message)

        # Send to the next player if it is not the player who just played.
        if this_player.id != active_player_id and active_player_id in self._clients:
            active_player_message = self._get_play_message(game.active_player, game)
            active_player_message['your_turn'] = True
            self._clients[active_player_id].sendMessage(active_player_message)

    def _get_play_message(self, player, game):
        return {
            'rt': RequestTypes.PLAY,
            'your_turn': player.id == game.active_player.id,
            'new_square': {
                'x': player.current_square.x,
                'y': player.current_square.y
            },
            'next_player': game.active_player.index,
            'hand': [{
                'name': card.name,
                'color': card.color
            } for card in player.hand],
            'game_over': game.is_over,
            'winners': game.winners,
            'active_trumps': [{
                'player_index': player.index,
                'player_name': player.name,
                'trumps_names': [trump.name for trump in player.affecting_trumps]
            } for player in game.players]
        }

    def _save_game(self, game):
        self._cache.save_game(game, self._game_id)

    def onClose(self, wasClean, code, reason):
        del Api._clients[self.id]

    def _send_all(self, message, excluded_players=set()):
        for player_id in self._cache.get_players_ids(self._game_id):
            player = self._clients.get(player_id, None)
            if player is not None and player_id not in excluded_players:
                player.sendMessage(message)

    def _send_all_others(self, message):
        self._send_all(message, excluded_players=set([self.id]))

    def _send_to(self, message, id):
        if id in self._clients:
            self._clients[id].sendMessage(message)

    def _send_all_error_to_display(self, message):
        self._send_all(self._format_error_to_display(message))

    def _format_error_to_display(self, message):
        return {'error_to_display': message}

    def _send_error(self, message):
        self.sendMessage(self._format_error(message))

    def _send_error_to_display(self, message):
        self.sendMessage(self._format_error_to_display(message))

    def _send_all_error(self, message):
        self._send_all(self._format_error(message))

    def _format_error(self, message):
        return{'error': message}

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if self._id is None:
            self._id = value
