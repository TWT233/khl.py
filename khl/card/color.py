"""helper wrapper for color in card message"""
import re
from typing import Tuple, Union, Optional

from .interface import _Representable


class Color(_Representable):
    """abstraction of color, provides helper functions"""

    def __init__(self, *rgb: int, hex_color: str = None):
        if (not rgb or len(rgb) != 3) and not hex_color:
            raise ValueError('rgb(as a tuple) or hex required')
        if hex_color:
            match = re.match(r'^#?([\da-fA-F]{2})([\da-fA-F]{2})([\da-fA-F]{2})$', hex_color)
            if not match:
                raise ValueError('unacceptable hex color')
            self._r, self._g, self._b = (int(match.group(i), 16) for i in (1, 2, 3))
        else:
            self._r, self._g, self._b = (self._rgb_check(i) for i in rgb)

    @staticmethod
    def _rgb_check(value: int) -> int:
        if not 0 <= value <= 255:
            raise ValueError(f'unacceptable rgb value, expected [0,255], exact {value}')
        return value

    @property
    def r(self) -> int:
        """red channel component in rgb model"""
        return self._r

    @r.setter
    def r(self, value: int):
        Color._rgb_check(value)
        self._r = value

    @property
    def g(self) -> int:
        """green channel component in rgb model"""
        return self._g

    @g.setter
    def g(self, value: int):
        Color._rgb_check(value)
        self._g = value

    @property
    def b(self) -> int:
        """blue channel component in rgb model"""
        return self._b

    @b.setter
    def b(self, value: int):
        Color._rgb_check(value)
        self._b = value

    def hex(self) -> str:
        """hex string form"""
        return self._repr

    @property
    def _repr(self) -> str:
        return f'#{self._r:02x}{self._g:02x}{self._b:02x}'


def make_color(color: Union[Color, Tuple[int, int, int], str, None]) -> Optional[Color]:
    """helper to unify all forms of color"""
    result = None
    if isinstance(color, Color):
        result = color
    elif isinstance(color, tuple):
        result = Color(*color)
    elif isinstance(color, str):
        result = Color(hex_color=color)
    return result
