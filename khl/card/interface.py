"""
Enum Types,
a helper function ``_repr()``,
the base class of all card components ``_Comm``
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Union, Dict, List


class ThemeTypes(Enum):
    NA = 'not_available'
    PRIMARY = 'primary'
    SECONDARY = 'secondary'
    SUCCESS = 'success'
    DANGER = 'danger'
    WARNING = 'warning'
    INFO = 'info'

    @property
    def repr(self):
        return self.value if self != ThemeTypes.NA else ''


class SizeTypes(Enum):
    NA = 'not_available'
    XS = 'xs'
    SM = 'sm'
    MD = 'md'
    LG = 'lg'

    @property
    def repr(self):
        return self.value if self != SizeTypes.NA else ''


class TextTypes(Enum):
    PLAIN = 'plain-text'
    KMD = 'kmarkdown'

    @property
    def repr(self):
        return self.value


class ClickTypes(Enum):
    LINK = 'link'
    RETURN_VAL = 'return-val'

    @property
    def repr(self):
        return self.value


class SectionModeTypes(Enum):
    LEFT = 'left'
    RIGHT = 'right'

    @property
    def repr(self):
        return self.value


class FileTypes(Enum):
    FILE = 'file'
    AUDIO = 'audio'
    VIDEO = 'video'

    @property
    def repr(self):
        return self.value


class CountdownModeTypes(Enum):
    DAY = 'day'
    HOUR = 'hour'
    SECOND = 'second'

    def repr(self):
        return self.value


def _repr(item) -> Union[str, Dict, List]:
    """a helper function for serialization"""
    return [_repr(i) for i in item] if isinstance(item, list) else getattr(item, 'repr', item)


class _Common(ABC):
    _type: str
    theme: ThemeTypes
    size: SizeTypes

    def __init__(self, theme: ThemeTypes, size: SizeTypes):
        super().__init__()
        self.theme = theme
        self.size = size

    @property
    def type(self) -> str:
        return self._type

    @property
    @abstractmethod
    def repr(self) -> Union[str, Dict, List]:
        raise NotImplementedError

    def _gen_dict(self, field_list: List) -> Dict:
        d = {}
        for k in field_list:
            if _repr(getattr(self, k, None)):
                d[k] = _repr(getattr(self, k))
        return d
