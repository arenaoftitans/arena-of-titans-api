from aot.cards.trumps.trumps import (
    ModifyNumberMoves,
    Trump,
    RemoveColor
)


trump_type_to_class = {
    'ModifyNumberMoves': ModifyNumberMoves,
    'RemoveColor': RemoveColor
}


__all__ = ['ModifyNumberMoves', 'RemoveColor', 'Trump', 'trump_type_to_class']
