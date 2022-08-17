"""all Type Enums and related helpers in card message"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import Union, Dict, List


class _Representable(ABC):
    """internal interface, can be cast to JSON"""

    @property
    @abstractmethod
    def _repr(self) -> Union[str, Dict, List]:
        """cast class object to JSON serializable representation"""
        raise NotImplementedError


class _TypeEnum(Enum):
    """base class of all types(involved in card components)

    remind: TypeEnum implements _repr but not inherits from Representable,
    since "TypeError: metaclass conflict:
    the metaclass of a derived class must be a (non-strict) subclass of the
    metaclasses of all its bases"
    """

    @property
    def _repr(self):
        return self.value


class Types:
    """contains all types used in card messages"""

    class Theme(_TypeEnum):
        """describes a component's theme, controls its color"""
        NA = ''
        PRIMARY = 'primary'
        SECONDARY = 'secondary'
        SUCCESS = 'success'
        DANGER = 'danger'
        WARNING = 'warning'
        INFO = 'info'
        NONE = 'none'

    class Size(_TypeEnum):
        """describes a component's size"""
        NA = ''
        XS = 'xs'
        SM = 'sm'
        MD = 'md'
        LG = 'lg'

    class Text(_TypeEnum):
        """which type of text"""
        PLAIN = 'plain-text'
        KMD = 'kmarkdown'

    class Click(_TypeEnum):
        """used in button, determines the behavior of button when clicked"""
        LINK = 'link'
        RETURN_VAL = 'return-val'

    class SectionMode(_TypeEnum):
        """used in section, arrangement of elements in"""
        LEFT = 'left'
        RIGHT = 'right'

    class File(_TypeEnum):
        """which type of file"""
        FILE = 'file'
        AUDIO = 'audio'
        VIDEO = 'video'

    class CountdownMode(_TypeEnum):
        """used in countdown module, determines its layout"""
        DAY = 'day'
        HOUR = 'hour'
        SECOND = 'second'


def _get_repr(item) -> Union[str, Dict, List]:
    """a helper function for serialization"""
    if isinstance(item, list):
        return [_get_repr(i) for i in item]
    return getattr(item, '_repr', item)


class _Common(_Representable, ABC):
    _type: str
    _theme: Types.Theme
    _size: Types.Size

    def __init__(self, theme: Union[Types.Theme, str, None], size: Union[Types.Size, str, None]):
        super().__init__()
        self._theme = Types.Theme(theme) if theme else None
        self._size = Types.Size(size) if size else None

    def _gen_dict(self, field_list: List) -> Dict:
        result = {}
        for k in field_list:
            # get repr of k/_k(private field with exported key)
            obj = _get_repr(getattr(self, k, None)) or _get_repr(getattr(self, '_' + k, None))
            if obj is not None:
                result[k] = obj
        return result


class _Module(_Common, ABC):
    ...


class _Struct(_Common, ABC):
    ...
