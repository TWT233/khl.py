from .card import Card
from .interface import _get_repr


class CardMessage(list):
    """
    can be cast to a list, the most outside wrapper for card message
    """

    def __init__(self, *cards: Card):
        super().__init__()
        self.extend(cards)

    def append(self, card: Card):
        super().append(card)

    def pop(self, __index=...) -> Card:
        return super().pop(__index)

    def __iter__(self):
        """hack for JSON serialization"""
        return iter([_get_repr(i) for i in self[:]])
