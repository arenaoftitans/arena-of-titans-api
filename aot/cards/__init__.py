from collections import namedtuple

from aot.cards.card import Card
from aot.cards.deck import Deck


SimpleCard = namedtuple('SimpleCard', ['name', 'color'])

__all__ = ['Card', 'Deck', 'SimpleCard']
