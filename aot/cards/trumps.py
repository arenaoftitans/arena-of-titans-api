class Trump:
    _name = ''
    _duration = 0
    _description = ''
    _must_target_player = False

    def __init__(
            self,
            name='',
            description='',
            duration=0,
            must_target_player=False):
        self._description = description
        self._duration = duration
        self._must_target_player = must_target_player
        self._name = name

    def consume(self):
        self._duration -= 1

    @property
    def duration(self):
        return self._duration


class ModifyNumberMoves(Trump):
    _delta_moves = 0

    def __init__(
            self,
            name='',
            duration=0,
            description='',
            must_target_player=False,
            delta_moves=0):
        super().__init__(
            name=name,
            duration=duration,
            description=description,
            must_target_player=must_target_player)
        self._delta_moves = delta_moves

    def affect(self, player):
        if player and self._duration > 0:
            player.modify_number_moves(self._delta_moves)
