import re
from typing import Tuple, Union, Optional

from .interface import Representable


class Color(Representable):
    def __init__(self, *rgb: int, hex: str = None):
        if (not rgb or len(rgb) != 3) and not hex:
            raise ValueError('rgb(as a tuple) or hex required')
        if hex:
            m = re.match(r'^#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$', hex)
            if not m:
                raise ValueError('unacceptable hex color')
            self._r, self._g, self._b = (int(m.group(i), 16) for i in (1, 2, 3))
        else:
            self._r, self._g, self._b = (self._rgb_check(i) for i in rgb)

    @staticmethod
    def _rgb_check(value: int) -> int:
        if not 0 <= value <= 255:
            raise ValueError(f'unacceptable rgb value, expected [0,255], exact {value}')
        return value

    @property
    def r(self) -> int:
        return self._r

    @r.setter
    def r(self, value: int):
        Color._rgb_check(value)
        self._r = value

    @property
    def g(self) -> int:
        return self._g

    @g.setter
    def g(self, value: int):
        Color._rgb_check(value)
        self._g = value

    @property
    def b(self) -> int:
        return self._b

    @b.setter
    def b(self, value: int):
        Color._rgb_check(value)
        self._b = value

    def hex(self) -> str:
        return self._repr

    @property
    def _repr(self) -> str:
        return f'#{self._r:02x}{self._g:02x}{self._b:02x}'


def make_color(color: Union[Color, Tuple[int, int, int], str, None]) -> Optional[Color]:
    result = None
    if isinstance(color, Color):
        result = color
    elif isinstance(color, tuple):
        result = Color(*color)
    elif isinstance(color, str):
        result = Color(hex=color)
    return result
