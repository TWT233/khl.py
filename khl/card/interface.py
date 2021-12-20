"""
Enum Types,
a helper function ``_repr()``,
the base class of all card components ``_Comm``
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Union, Dict, List


class Representable(ABC):
    @property
    @abstractmethod
    def _repr(self) -> Union[str, Dict, List]:
        """cast class object to JSON serializable representation"""
        raise NotImplementedError


class _TypeEnum(Enum):
    """base class of all types(involved in card components)

    REMIND: TypeEnum implements _repr but not inherits from Representable, since
    " TypeError: metaclass conflict:
    the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases "
    """

    @property
    def _repr(self):
        return self.value


class ThemeTypes(_TypeEnum):
    NA = ''
    PRIMARY = 'primary'
    SECONDARY = 'secondary'
    SUCCESS = 'success'
    DANGER = 'danger'
    WARNING = 'warning'
    INFO = 'info'


class SizeTypes(_TypeEnum):
    NA = ''
    XS = 'xs'
    SM = 'sm'
    MD = 'md'
    LG = 'lg'


class TextTypes(_TypeEnum):
    PLAIN = 'plain-text'
    KMD = 'kmarkdown'


class ClickTypes(_TypeEnum):
    LINK = 'link'
    RETURN_VAL = 'return-val'


class SectionModeTypes(_TypeEnum):
    LEFT = 'left'
    RIGHT = 'right'


class FileTypes(_TypeEnum):
    FILE = 'file'
    AUDIO = 'audio'
    VIDEO = 'video'


class CountdownModeTypes(_TypeEnum):
    DAY = 'day'
    HOUR = 'hour'
    SECOND = 'second'


def _get_repr(item) -> Union[str, Dict, List]:
    """a helper function for serialization"""
    return [_get_repr(i) for i in item] if isinstance(item, list) else getattr(item, '_repr', item)


class _Common(Representable, ABC):
    _type: str
    _theme: ThemeTypes
    _size: SizeTypes

    def __init__(self, theme: Union[ThemeTypes, str, None], size: Union[SizeTypes, str, None]):
        super().__init__()
        self._theme = ThemeTypes(theme) if theme else None
        self._size = SizeTypes(size) if size else None

    def _gen_dict(self, field_list: List) -> Dict:
        d = {}
        for k in field_list:
            # get repr of k/_k(private field with exported key)
            obj = _get_repr(getattr(self, k, None)) or _get_repr(getattr(self, '_' + k, None))
            if obj is not None:
                d[k] = obj
        return d


class _Element(_Common, ABC):
    ...


class _Module(_Common, ABC):
    ...
