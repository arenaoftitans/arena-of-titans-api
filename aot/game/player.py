class Player:
    BOARD_ARM_WIDTH_AND_MODULO = 4
    BOARD_ARM_LENGTH_AND_MAX_Y = 8
    MAX_NUMBER_MOVE_TO_PLAY = 2

    _aim = set()
    _affecting_trumps = []
    _board = None
    _can_play = False
    _current_square = None
    _deck = None
    _has_won = False
    _id = ''
    _index = -1
    _last_square_previous_turn = None
    _name = ''
    _number_moves_to_play = 2
    _rank = -1
    

    def __init__(self, name, id, index):
        self._name = name
        self._id = id
        self._index = index

        self._affecting_trumps = []

    def set(self, board, deck):
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

    def play_card(self, card, square, check_move=True):
        if card and check_move:
            possible_squares = self.view_possible_squares(card)
        elif not card and check_move:
            return
        else:
            possible_squares = set()
        x, y = square
        dest_square = self._board[x, y]
        if dest_square in possible_squares or not check_move:
            self._deck.play(card)
            self.move(dest_square)
        self._complete_action()

    def _complete_action(self):
        self._number_moves_played += 1
        self._can_play = self._number_moves_played < self._number_moves_to_play

    def discard(self, card):
        self._deck.play(card)
        self._complete_action()

    def pass_turn(self):
        self._can_play = False

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
        self._number_moves_played = 0
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
            if trump.duration == 0:
                self._affecting_trumps.remove(trump)

    def _revert_to_default(self):
        self._deck.revert_to_default()
        self._number_moves_to_play = self.MAX_NUMBER_MOVE_TO_PLAY

    def modify_number_moves(self, delta):
        self._number_moves_to_play += delta

    def affect_by(self, trump):
        self._affecting_trumps.append(trump)
        if self._can_play:
            trump.affect(self)

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
    def current_square(self):
        return self._current_square

    @property
    def deck(self):
        return self._deck

    @property
    def hand(self):
        return self._deck.hand

    @property
    def id(self):
        return self._id

    @property
    def index(self):
        return self._index

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
    def trumps(self):
        return [
           {
               "name":"Reinforcements",
               "description":"Allow the player to play one more move.",
               "duration":0,
               "cost":0,
               "repeat_for_each_color":False,
               "must_target_player":False
           },
           {
               "name":"Tower BLACK",
               "description":"Prevent the player to move on some colors.",
               "duration":0,
               "cost":0,
               "repeat_for_each_color":False,
               "must_target_player":True
           },
           {
               "name":"Tower BLUE",
               "description":"Prevent the player to move on some colors.",
               "duration":0,
               "cost":0,
               "repeat_for_each_color":False,
               "must_target_player":True
           },
           {
               "name":"Tower RED",
               "description":"Prevent the player to move on some colors.",
               "duration":0,
               "cost":0,
               "repeat_for_each_color":False,
               "must_target_player":True
           },
           {
               "name":"Tower YELLOW",
               "description":"Prevent the player to move on some colors.",
               "duration":0,
               "cost":0,
               "repeat_for_each_color":False,
               "must_target_player":True
           }
        ]
