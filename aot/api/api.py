from autobahn.asyncio.websocket import WebSocketServerProtocol
import base64
import json
import uuid

from aot import get_game
from aot import get_number_players
from aot.api.api_cache import ApiCache
from aot.api.utils import RequestTypes


class Api(WebSocketServerProtocol):
    # Class variables.
    _clients = {}
    _cache = ApiCache()

    # Instance variables
    _game_id = None
    _message = None

    def sendMessage(self, message):
        if isinstance(message, str):
            message = message.encode('utf-8')
        else:
            message = json.dumps(message).encode('utf-8')
        if isinstance(message, bytes):
            super().sendMessage(message)

    def onOpen(self):
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
        return self._cache.is_new_game(self._game_id) or self._cache.has_opened_slots(self._game_id)

    def _initialize_cache(self):
        initiliazed_game = {
            'rt': RequestTypes.GAME_INITIALIZED.value,
            'is_game_master': False,
            'game_id': self._game_id
        }
        if self._cache.is_new_game(self._game_id):
            self._cache.init(self._game_id, self.id)
            initiliazed_game['is_game_master'] = True
        else:
            self._cache.save_session(self._game_id, self.id)
            initiliazed_game['slots'] = self._cache.get_slots(self._game_id)

        initiliazed_game['index'] = self._affect_current_slot()
        return initiliazed_game

    def _affect_current_slot(self):
        return self._cache.affect_next_slot(self._game_id, self.id)

    def _creating_game(self):
        return not self._cache.has_game_started(self._game_id)

    def _process_create_game_request(self):
        if not self._cache.is_game_master(self._game_id, self.id) and \
                self.message['rt'] != RequestTypes.SLOT_UPDATED:
            self._send_error('Only the game master can create the game')
        else:
            self._do_create_game_request()

    def _do_create_game_request(self):
        rt = self.message['rt']
        response = ''
        if rt in (RequestTypes.ADD_SLOT.value, RequestTypes.SLOT_UPDATED.value):
            slot = self.message['slot']
            if rt == RequestTypes.ADD_SLOT.value:
                self._cache.add_slot(self._game_id, slot)
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
        elif rt == RequestTypes.CREATE_GAME:
            players_description = self.message['create_game_request']
            self._send_all(self._initialize_game(players_description))
        else:
            self._send_all_error('Unknown request')

        return response

    def _initialize_game(self, players_description):
        players_description = [player for player in players_description if player['name']]
        if len(players_description) < 2:
            self._send_all_error_to_display('Not enough players. 2 Players are at least required to start a game')
        elif len(players_description) > get_number_players():
            self._send_all_error_to_display('To many players. 8 Players max.')
        else:
            self._create_game(players_description)
            self._cache.game_has_started(self.game_id)

    def _create_game(self, players_description):
        players_ids = self._cache.get_players_ids(self.game_id)
        for player in players_description:
            index = player['index']
            player['id'] = players_ids[index]

        game = get_game(players_description)
        self._cache.save_game(game, self.game_id)
        self._send_game_created_message(game)

    def _send_game_created_message(self, game):
        game_created = {
            'rt': RequestTypes.CREATE_GAME,
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
            } for player in game.players]
        }
        self._send_all(game_created)
        for player in game.players:
            message = {
                'hand': [{
                    'name': card.name,
                    'color': card.color
                } for card in player.hand],
                'trumps': player.trumps
            }
            self._send_to(message, player.id)

    def _process_play_request(self):
        game = self._load_game()
        if _is_player_id_correct(game):
            self._play_game(game)
            self._save_game(game)
        else:
            self._send_error_to_display('Not Your Turn')

    def _load_game(self):
        return self._cache.get_match(self._game_id)

    def _is_player_id_correct(self, game):
        return self.id is not None and self.id == game.active_player.id

    def _play_game(self, game):
        rt = self.message['rt']
        play_request = self.message.get('play_request', {})
        if rt == RequestTypes.VIEW_POSSIBLE_SQUARES:
            card = self._get_card(play_request)
            self.sendMessage(game.view_possible_square(card))
        if rt == RequestTypes.PLAY:
            this_player = game.active_player
            self._play_card(game, play_request)
            self._send_message_current_player(this_player, game.active_player)

    def _send_message_current_player(self, this_player, active_player):
        player_id = active_player.id
        this_player_message = self._get_play_message(this_player)
        self.sendMessage(this_player_message)
        if player_id in self._clients:
            active_player_message = self._get_play_message(active_player)
            active_player_message['your_turn'] = True
            self._clients[player_id].sendMessage(active_player_message)

    def _get_play_message(self, player):
        return {
            'rt': RequestTypes.PLAY,
            'your_turn': player.id == self.id,
            'new_square': {
                'x': player.current_square.x,
                'y': player.current_square.y
            },
            'cards': [{
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

    def _get_card(self, play_request):
        card_name = play_request.get('card_name', None)
        card_color = play_request.get('card_color', None)
        return card_name, card_color

    def _play_card(self, game, play_request):
        if play_request.get('pass', False):
            game.pass_turn()
        elif play_request.get('discard', False):
            card = self._get_card(play_request)
            game.discard(card)
        else:
            card = self._get_card(play_request)
            square = self._get_square(play_request)
            game.play_card(card, square)

    def _get_square(self, play_request):
        x = play_request.get('x', None)
        y = play_request.get('y', None)
        return x, y

    def _save_game(self, game):
        self._cache.save_match(game, self._game_id)

    def onClose(self, wasClean, code, reason):
        del Api._clients[self.id]

    def _get_card(self, msg):
        if 'value' in msg:
            card = msg['value']
        else:
            card = msg['card']
        color, name = card.split('_')
        color = color.lower()
        name = name.lower().title()
        return name, color

    def _send_all(self, message, excluded_players=set()):
        for player_id in self._cache.get_players_ids(self._game_id):
            player = self._clients.get(player_id, None)
            if player is not None and player_id not in excluded_players:
                player.sendMessage(message)

    def _send_to(self, message, id):
        if id in self._clients:
            self._clients[id].sendMessage(message)

    def _send_all_error_to_display(self, message):
        self._send_all(self._format_error_to_display(message))

    def _format_error_to_display(self, message):
        return {'error_to_display': message}

    def _send_error(self, message):
        self.sendMessage(self._format_error(message))

    def _send_all_error(self, message):
        self._send_all(self._format_error(message))

    def _format_error(self, message):
        return{'error': message}

    @property
    def id(self):
        return self._wskey
