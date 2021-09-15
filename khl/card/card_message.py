from typing import List, Dict

from .card import Card
from .interface import _repr


class CardMessage:
    """
    can be cast to a dict, the most outside wrapper for card message
    """
    cards: List[Card]

    def __init__(self, cards: List[Card] = ()):
        self.cards = list(cards)

    def append_card(self, card: Card):
        self.cards.append(card)

    def pop_card(self, index: int = None) -> Card:
        return self.cards.pop(index)

    @property
    def repr(self) -> List[Dict]:
        return _repr(self.cards)
