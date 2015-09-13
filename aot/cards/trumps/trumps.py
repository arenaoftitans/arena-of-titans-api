from aot.board import Color


class Trump:
    _name = ''
    _duration = 0
    _description = ''
    _must_target_player = False

    def __init__(
            self,
            cost=5,
            name='',
            description='',
            duration=0,
            must_target_player=False):
        self._cost = cost
        self._description = description
        self._duration = duration
        self._must_target_player = must_target_player
        self._name = name

    def consume(self):
        self._duration -= 1

    @property
    def cost(self):
        return self._cost

    @property
    def description(self):
        return self._description

    @property
    def duration(self):
        return self._duration

    @property
    def must_target_player(self):
        return self._must_target_player

    @property
    def name(self):
        return self._name


class ModifyNumberMoves(Trump):
    _delta_moves = 0

    def __init__(
            self,
            cost=5,
            name='',
            duration=0,
            description='',
            must_target_player=False,
            delta_moves=0):
        super().__init__(
            cost=cost,
            name=name,
            duration=duration,
            description=description,
            must_target_player=must_target_player)
        self._delta_moves = delta_moves

    def affect(self, player):
        if player and self._duration > 0:
            player.modify_number_moves(self._delta_moves)


class RemoveColor(Trump):
    _colors = set()

    def __init__(
            self,
            cost=5,
            name='',
            duration=0,
            description='',
            must_target_player=False,
            color=None,
            colors=None):
        super().__init__(
            cost=cost,
            name=name,
            duration=duration,
            description=description,
            must_target_player=must_target_player)
        self._colors = set()
        if colors is not None:
            for color in colors:
                self._add_color(color)
        if color is not None:
            self._add_color(color)

    def _add_color(self, color):
        if isinstance(color, str):
            self._colors.add(Color[color.upper()])
        else:
            self._colors.add(color)

    def affect(self, player):
        for color in self._colors:
            player.deck.remove_color_from_possible_colors(color)
