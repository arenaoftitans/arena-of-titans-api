#
#  Copyright (C) 2015-2020 by Arena of Titans Contributors.
#
#  This file is part of Arena of Titans.
#
#  Arena of Titans is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Arena of Titans is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Arena of Titans. If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from types import MappingProxyType

import daiquiri

from ..cards import Card
from .constants import EffectTypes
from .exceptions import TrumpHasNoEffectError

logger = daiquiri.getLogger(__name__)


class TrumpEffect(metaclass=ABCMeta):
    def __init__(
        self,
        trump: Trump,  # noqa: F821 undefined name
        *,
        target: Player,  # noqa: F821 undefined name
        initiator: Player,  # noqa: F821 undefined name
        context: dict,
        effect_type: EffectTypes,
    ):
        self._trump = trump
        self._target = target
        self._initiator = initiator
        self._context = context
        self._duration = self._trump.duration
        self._effect_type = effect_type

    def allow_trump_to_affect(self, trump):
        return self._trump.allow_trump_to_affect(trump)

    @abstractmethod
    def apply(self):
        pass

    def teardown(self, trumps):
        # By default there is nothing to do.
        return trumps

    def consume(self):
        self._duration -= 1

    @property
    def context(self):
        return MappingProxyType(self._context)

    @property
    def color(self):
        return self._trump.color

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, value):
        self._duration = value

    @property
    def effect_type(self):
        return self._effect_type

    @property
    def name(self):
        return self._trump.name

    @property
    def is_player_visible(self):
        return self._trump.is_player_visible

    def __eq__(self, other: TrumpEffect):
        if self is other:
            return True

        return (
            self.__class__ == other.__class__
            and self._trump == other._trump
            and self._target == other._target
            and self._initiator == other._initiator
            and self._context == other._context
            and self._duration == other._duration
        )

    def __str__(self):
        return (
            f"{self.__class__.__name__}<trump={self._trump}, target={self._target}, "
            f"initiator={self._initiator}>"
        )

    def __repr__(self):
        return str(self)


class ModifyNumberMovesEffect(TrumpEffect):
    def apply(self):
        self._target.modify_number_moves(self._trump.delta_moves)


class ModifyCardColorEffect(TrumpEffect):
    def apply(self):
        def filter_(card: Card):
            return card.name in self._trump.card_names

        self._target.modify_card_colors(self._trump.colors, filter_=filter_)


class CannotBeAffectedByTrumpsEffect(TrumpEffect):
    def apply(self):
        pass


class ChangeSquareEffect(TrumpEffect):
    def apply(self):
        x, y = self._context["square"]["x"], self._context["square"]["y"]
        self._context["board"].change_color_of_square(x, y, self._context["square"]["color"])


class ModifyCardNumberMovesEffect(TrumpEffect):
    def apply(self):
        def filter_(card: Card):
            return card.name in self._trump.card_names

        self._target.modify_card_number_moves(self._trump.delta_moves, filter_=filter_)


class AddSpecialActionsToCardEffect(TrumpEffect):
    def apply(self):
        self._target.set_special_actions_to_cards_in_deck(
            self._trump.card_names, self._trump.spectial_action_despriptions
        )


class ModifyTrumpDurationsEffect(TrumpEffect):
    def apply(self):
        def filter_(effect: TrumpEffect):
            return (
                effect is not self
                and effect._trump.name in self._trump.trump_names
                and self._trump.name not in effect._trump.prevent_trumps_to_modify
            )

        # Currently we can only apply this to affecting trumps.
        affected_trumps = [trump for trump in self._target.trump_effects if filter_(trump)]
        if len(affected_trumps) == 0:
            raise TrumpHasNoEffectError

        self._target.modify_trump_effects_durations(
            self._trump.delta_duration, filter_=filter_,
        )


class PreventTrumpActionEffect(TrumpEffect):
    def apply(self):
        logger.info(
            f"Tried to apply effect for {self.__class__.__name__}. This has no effect. "
            f"It is currently only supported for powers and must be enabled in their setup method."
        )


class RemoveColorEffect(TrumpEffect):
    def apply(self):
        for color in [self._trump.color, *self._trump.colors]:
            if color:
                self._target.deck.remove_color_from_possible_colors(color)


class StealPowerEffect(TrumpEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We need to store it here because the stolen power must be used in the player class too.
        self._context["stolen_power"] = self._target.power

    def apply(self):
        stolen_power = self._context["stolen_power"]
        if not stolen_power.passive:
            stolen_power = stolen_power.cancel_cost()
            self._context["stolen_power"] = stolen_power
        self._initiator.setup_new_power(stolen_power)
        if stolen_power.passive:
            self._initiator.play_trump(stolen_power, target=self._initiator, context=self._context)

    def teardown(self, trumps):
        stolen_power = self._context["stolen_power"]
        return stolen_power.teardown(trumps)


class TeleportEffect(TrumpEffect):
    def apply(self):
        if self._context["square"] in self.view_possible_squares():
            self._target.move(self._context["square"])

    def view_possible_squares(self):
        card = Card(
            self._context["board"],
            color=self._trump.color,
            complementary_colors=self._trump.colors,
            name="Teleportation",
            movements_types=["line", "diagonal"],
            number_movements=self._trump.distance,
        )

        origin_square = self._target.current_square
        return card.move(origin_square)


class VoidEffect(TrumpEffect):
    def apply(self):
        logger.debug("Void trump called.")
