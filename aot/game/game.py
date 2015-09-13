import aot


class Game:
    _active_player = None
    _board = None
    _is_over = False
    _next_rank_available = 1
    _players = []
    _winners = []

    def __init__(self, board, players):
        self._active_player = players[0]
        self._active_player.init_turn()
        self._board = board
        self._is_over = False
        self._players = players
        self._next_rank_available = 1
        self._winners = []
        for player in self._players:
            deck = aot.get_deck(board)
            player.set(board, deck)

    def view_possible_squares(self, card):
        return self._active_player.view_possible_squares(card)

    def play_card(self, card, square, check_move=True):
        self._active_player.play_card(card, square, check_move=check_move)
        self._continue_game_if_enough_players()

    def can_move(self, card, square):
        return self._active_player.can_move(card, square)

    def get_square(self, x, y):
        return self._board[x, y]

    def _continue_game_if_enough_players(self):
        if self._has_enough_players_to_continue():
            self._active_player = self._find_next_player()
        else:
            self._is_over = True

    def _has_enough_players_to_continue(self):
        return len([player for player in self._players
            if player is not None and not player.has_won]) > 1

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
            if player is not None and not player.has_won:
                break
            index_next_player += 1

        return index_next_player

    def _add_to_winners(self, player):
        player.wins(rank=self._next_rank_available)
        self._next_rank_available += 1
        self._winners.append(player)
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

    @property
    def active_player(self):
        return self._active_player

    @property
    def is_over(self):
        return self._is_over

    @property
    def players(self):
        return self._players

    @property
    def winners(self):
        return [player.name for player in self._winners]
