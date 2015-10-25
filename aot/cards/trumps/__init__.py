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
    def __getitem__(self, key):
        if isinstance(key, int):
            super()[key]
        else:
            for trump in self:
                if trump.name == key:
                    return trump_type_to_class[trump.type](**trump.args)
        raise KeyError('No trump found for key: {}'.format(key))


__all__ = ['ModifyNumberMoves', 'RemoveColor', 'SimpleTrump', 'Trump', 'TrumpList']
