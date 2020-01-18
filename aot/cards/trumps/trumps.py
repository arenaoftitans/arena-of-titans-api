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

import random
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from typing import List, Tuple

from ...board import Color, all_colors
from .. import Card
from .constants import TargetTypes
from .exceptions import TrumpHasNoEffect
from .utils import return_trump_infos


class Trump(metaclass=ABCMeta):
    target_type = TargetTypes.player

    _name = ""
    _duration = 0
    _description = ""
    _must_target_player = False
    _initiator = None
    #: List of trumps names that cannot modify this trump.
    #: This is also used to force a trump to act against a CannotBeAffectedByTrumps.
    _prevent_trumps_to_modify: Tuple[str] = ()

    def __init__(
        self,
        duration=0,
        cost=5,
        description="",
        must_target_player=False,
        name="",
        color=None,
        temporary=False,
        prevent_trumps_to_modify=None,
        **kwargs,
    ):
        self._cost = cost
        self._description = description
        self._duration = duration
        self._must_target_player = must_target_player
        self._name = name
        self._color = color
        if isinstance(color, str):
            self._color = Color[color]
        self._temporary = temporary
        self._prevent_trumps_to_modify = (
            prevent_trumps_to_modify if prevent_trumps_to_modify else ()
        )

    def _set_colors(self, color, colors):
        self._colors = set()
        if colors is not None:
            for color in colors:
                self._add_color(color)
        if color is not None:
            self._add_color(color)

    def _add_color(self, color):
        if isinstance(color, str):  # pragma: no cover
            self._colors.add(Color[color])
        else:  # pragma: no cover
            self._colors.add(color)

    @abstractmethod
    def affect(self, **kwargs):
        pass

    def allow_trump_to_affect(self, trump):
        return True

    def consume(self):
        self._duration -= 1

    def __str__(self):  # pragma: no cover
        return (
            f"{type(self).__name__}(duration={self.duration}, cost={self.cost}, "
            f"must_target_player={self.must_target_player}, name={self.name})"
        )

    def __repr___(self):  # pragma: no cover
        return str(self)

    @property
    def color(self):
        return self._color

    @property
    def cost(self):  # pragma: no cover
        return self._cost

    @cost.setter
    def cost(self, value):  # pragma: no cover
        self._cost = value

    @property
    def description(self):  # pragma: no cover
        return self._description

    @property
    def duration(self):  # pragma: no cover
        if self._duration == float("inf"):
            return
        return self._duration

    @duration.setter
    def duration(self, value):
        if not isinstance(value, int):
            raise ValueError("Duration must be an int")

        self._duration = value

    @property
    def must_target_player(self):  # pragma: no cover
        return self._must_target_player

    @property
    def name(self):  # pragma: no cover
        return self._name

    @property
    def initiator(self):  # pragma: no cover
        return self._initiator

    @initiator.setter
    def initiator(self, initiator):  # pragma: no cover
        self._initiator = initiator

    @property
    def temporary(self):
        return self._temporary


class ModifyNumberMoves(Trump):
    _delta_moves = 0

    def __init__(
        self,
        cost=5,
        delta_moves=0,
        description="",
        duration=0,
        name="",
        color=None,
        must_target_player=False,
        **kwargs,
    ):
        super().__init__(
            cost=cost,
            description=description,
            duration=duration,
            must_target_player=must_target_player,
            name=name,
            color=color,
            **kwargs,
        )
        self._delta_moves = delta_moves

    @return_trump_infos
    def affect(self, *, player):
        if player and self._duration > 0:
            player.modify_number_moves(self._delta_moves)


class ModifyCardColors(Trump):
    _colors = None
    _card_names = None

    def __init__(
        self,
        card_names=None,
        cost=5,
        add_colors=None,
        description="",
        duration=0,
        name="",
        color=None,
        must_target_player=False,
        **kwargs,
    ):
        super().__init__(
            cost=cost,
            description=description,
            duration=duration,
            must_target_player=must_target_player,
            name=name,
            color=color,
            **kwargs,
        )
        self._set_colors(None, add_colors)
        self._card_names = card_names

    @return_trump_infos
    def affect(self, *, player):
        filter_ = None
        if self._card_names is not None:

            def filter_(card: Card):
                return card.name in self._card_names

        if player and self._duration > 0:
            player.modify_card_colors(self._colors, filter_=filter_)


class CannotBeAffectedByTrumps(Trump):
    _trump_names = []

    def __init__(
        self, *, trump_names, **kwargs,
    ):
        """Prevent the given trumps to have an effect."""
        super().__init__(**kwargs)
        self._trump_names = trump_names

    @return_trump_infos
    def affect(self, *, player):
        pass

    def allow_trump_to_affect(self, trump: Trump):
        # If trump_names is not defined, we consider that not trump can affect the player.
        if not self._trump_names:
            return False

        # ``trump.name in self._trump_names`` says the trump has no effect.
        # but ``self.name in trump._prevent_trumps_to_modify`` says
        # the trump has an effect nonetheless.
        # So we randomly pick an outcome.
        if trump.name in self._trump_names and self.name in trump._prevent_trumps_to_modify:
            return random.choice((False, True))  # noqa: S311 (random generator)

        if trump.name in self._trump_names:
            return False
        return True

    @property
    def is_affecting_all_trumps(self):
        return not self._trump_names


class ChangeSquare(Trump):
    target_type = TargetTypes.board

    def __init__(
        self, **kwargs,
    ):
        """Change a square.

        We currently only support changing the color.
        """
        super().__init__(**kwargs)

    @return_trump_infos
    def affect(self, *, x, y, board, color):
        square = board[x, y]
        square.color = color


class ModifyCardNumberMoves(Trump):
    _delta_moves = 0
    _card_names = None

    def __init__(
        self,
        card_names=None,
        cost=5,
        delta_moves=0,
        description="",
        duration=0,
        name="",
        color=None,
        must_target_player=False,
        **kwargs,
    ):
        super().__init__(
            cost=cost,
            description=description,
            duration=duration,
            must_target_player=must_target_player,
            name=name,
            color=color,
            **kwargs,
        )
        self._card_names = card_names
        self._delta_moves = delta_moves

    @return_trump_infos
    def affect(self, *, player):
        filter_ = None
        if self._card_names is not None:

            def filter_(card: Card):
                return card.name in self._card_names

        if player and self._duration > 0:
            player.modify_card_number_moves(self._delta_moves, filter_=filter_)


class AddSpecialActionsToCard(Trump):
    _card_names = None
    _special_actions = None

    def __init__(
        self,
        card_names=None,
        special_actions=None,
        cost=5,
        description="",
        duration=0,
        name="",
        color=None,
        must_target_player=False,
        **kwargs,
    ):
        super().__init__(
            cost=cost,
            description=description,
            duration=duration,
            must_target_player=must_target_player,
            name=name,
            color=color,
            **kwargs,
        )
        from aot.cards.trumps import TrumpList, SimpleTrump

        self._card_names = card_names
        self._special_actions = TrumpList()
        for action in special_actions:
            type_ = action["parameters"]["type"]
            del action["parameters"]["type"]
            action.update(action["parameters"])
            del action["parameters"]
            self._special_actions.append(
                SimpleTrump(type=type_, name=action["name"], color=None, args=action,)
            )

    @return_trump_infos
    def affect(self, *, player):
        player.set_special_actions_to_cards_in_deck(self._card_names, self._special_actions)


class ModifyTrumpDurations(Trump):
    def __init__(
        self,
        trump_names=None,
        cost=5,
        delta_duration=0,
        description="",
        duration=0,
        name="",
        color=None,
        must_target_player=False,
        temporary=False,
        **kwargs,
    ):
        super().__init__(
            cost=cost,
            description=description,
            duration=duration,
            must_target_player=must_target_player,
            name=name,
            color=color,
            temporary=temporary,
            **kwargs,
        )
        self._delta_duration = delta_duration
        self._trump_names = trump_names

    @return_trump_infos
    def affect(self, *, player):
        if self._trump_names is None:

            def filter_(trump: "Trump"):
                return False

        else:

            def filter_(trump: "Trump"):
                return (
                    trump is not self
                    and trump.name in self._trump_names
                    and self.name not in trump._prevent_trumps_to_modify
                )

        if player and self._duration > 0:
            # Currently we can only apply this to affecting trumps.
            affected_trumps = [trump for trump in player.affecting_trumps if filter_(trump)]
            if len(affected_trumps) == 0:
                raise TrumpHasNoEffect

            player.modify_affecting_trump_durations(
                self._delta_duration, filter_=filter_,
            )


class PreventTrumpAction(Trump):
    _prevent_for_trumps: Tuple[str] = ()
    _enable_for_trumps: Tuple[str] = ()

    def __init__(
        self, *, prevent_for_trumps: List[str], enable_for_trumps: List[str], **kwargs,
    ):
        """Prevent the normal behavior of a trump.

        For instance with the power *Impassable*, the towers and fortresses played are immune
        to the *Ram* trump. This trump is meant to make this possible.

        Args:
            prevent_for_trumps:  List of trump names that cannot be applied to
                ``enable_for_trumps``
            enable_for_trumps: List of trump names to modify. Only the trumps with these names
                will be modified and cannot be affected by ``prevent_trumps``.
        """
        super().__init__(**kwargs)
        self._prevent_for_trumps = tuple(prevent_for_trumps)
        self._enable_for_trumps = tuple(enable_for_trumps)

    @return_trump_infos
    def affect(self, *, player):
        for trump in player.available_trumps:
            if trump.name in self._enable_for_trumps:
                trump.args["prevent_trumps_to_modify"] = self._prevent_for_trumps


class RemoveColor(Trump):
    _colors = set()

    def __init__(
        self,
        color=None,
        colors=None,
        cost=5,
        description="",
        duration=0,
        name="",
        must_target_player=False,
        **kwargs,
    ):
        super().__init__(
            cost=cost,
            description=description,
            duration=duration,
            must_target_player=must_target_player,
            name=name,
            color=color,
            **kwargs,
        )
        self._set_colors(color, colors)

    @return_trump_infos
    def affect(self, *, player):
        for color in self._colors:
            player.deck.remove_color_from_possible_colors(color)


class Teleport(Trump):
    # Instance variables
    _distance = 0
    _colors = None

    def __init__(
        self,
        board=None,
        distance=0,
        color=None,
        colors=None,
        cost=10,
        description="",
        duration=0,
        name="",
        must_target_player=False,
        **kwargs,
    ):
        super().__init__(
            cost=cost,
            description=description,
            duration=duration,
            must_target_player=must_target_player,
            name=name,
            color=color,
            **kwargs,
        )
        self._distance = distance
        if color is None and colors is None:
            self._colors = deepcopy(all_colors)
        else:
            self._set_colors(color, colors)
        # We use a card to get the list of possible squares for teleportation.
        self._card = Card(
            board,
            color=next(iter(self._colors)),
            complementary_colors=self._colors,
            name="Teleportation",
            movements_types=["line", "diagonal"],
            number_movements=distance,
        )

    @return_trump_infos
    def affect(self, *, player, square):
        origin_square = player.current_square
        if player and square in self._card.move(origin_square):
            player.move(square)

    def view_possible_squares(self, player):
        return self._card.move(player.current_square)

    @property
    def require_target_square(self):
        return True
