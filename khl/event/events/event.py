from abc import ABC


class AbstractEvent(ABC):
    def __init__(self, raw: dict):
        self._raw = raw

    @property
    def raw(self):
        return self._raw
