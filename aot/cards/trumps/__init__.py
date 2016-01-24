from collections import namedtuple

from aot.cards.trumps.trumps import (
    ModifyNumberMoves,
    Trump,
    RemoveColor
)


trump_type_to_class = {
    'ModifyNumberMoves': ModifyNumberMoves,
    'RemoveColor': RemoveColor
}

SimpleTrump = namedtuple('SimpleTrump', 'type name args')


class TrumpList(list):
    def __init__(self, trumps=None):
        if trumps is not None:
            super().__init__(trumps)
        else:
            super().__init__()

    def __getitem__(self, key):
        if key is None or isinstance(key, str):
            for trump in self:
                if trump.name == key:
                    return trump_type_to_class[trump.type](**trump.args)
        elif isinstance(key, int):
            return super().__getitem__(key)
        elif isinstance(key, slice):
            return TrumpList(trumps=super().__getitem__(key))


__all__ = ['ModifyNumberMoves', 'RemoveColor', 'SimpleTrump', 'Trump', 'TrumpList']
