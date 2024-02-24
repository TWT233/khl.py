from abc import ABC


class BaseEvent(ABC):
    """base event"""

    def __init__(self, raw: dict):
        self._raw = raw

    @property
    def raw(self):
        """return the event raw body"""
        return self._raw
