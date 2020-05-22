#
#  Copyright (C) 2015-2020 by Last Run Contributors.
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

from abc import ABCMeta, abstractmethod


class BaseTrumpsLikeList(metaclass=ABCMeta):
    def __init__(self, trumps_like):
        self._trumps_like = list(trumps_like)

    def append(self, trump):
        self._trumps_like.append(trump)

    @abstractmethod
    def _get_matching_trumps_like(self, name, color):
        pass

    def _get_matching_trump_like(self, name, color):
        matching_trumps = self._get_matching_trumps_like(name, color)
        if len(matching_trumps) == 0:
            raise IndexError(f"No trump found for {name} and {color} in {self.__class__.__name__}.")
        elif len(matching_trumps) > 1:
            raise IndexError(
                f"More than one trump found for {name} and {color} in {self.__class__.__name__}."
            )

        return matching_trumps[0]

    def __getitem__(self, item):
        if isinstance(item, int):
            return self._trumps_like[item]
        elif isinstance(item, (list, tuple)):
            name, color = item
            return self._get_matching_trump_like(name, color)

        raise IndexError(f"Cannot find trumps by {item}")

    def __len__(self):
        return len(self._trumps_like)

    def __str__(self):
        return str(self._trumps_like)

    def __repr__(self):
        return str(self)


class SpecialActionsList(BaseTrumpsLikeList):
    def _get_matching_trumps_like(self, name, color):
        return [action for action in self._trumps_like if action.trump.name.lower() == name.lower()]


class TrumpsList(BaseTrumpsLikeList):
    def _get_matching_trumps_like(self, name, color):
        return [
            trump
            for trump in self._trumps_like
            if trump.name.lower() == name.lower() and trump.color == color
        ]
