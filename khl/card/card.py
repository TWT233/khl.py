import re
from typing import List, Union, Dict, Tuple, Optional

from .interface import ThemeTypes, SizeTypes, _Common
from .module import Module


class Color:
    def __init__(self, rgb: Tuple[int, int, int] = None, *, hex: str = None):
        if (not rgb or len(rgb) != 3) and not hex:
            raise ValueError('rgb(as a tuple) or hex required')
        if hex:
            m = re.match(r'^#?([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$', hex)
            if not m:
                raise ValueError('unacceptable hex color')
            r = int(m.group(1), 16)
            g = int(m.group(2), 16)
            b = int(m.group(3), 16)
        else:
            [Color.rgb_check(i) for i in rgb]
            r, g, b = rgb
        self._r = r
        self._g = g
        self._b = b

    @staticmethod
    def rgb_check(value: int):
        if not 0 <= value <= 255:
            raise ValueError(f'unacceptable rgb value, expected [0,255], exact {value}')

    @property
    def r(self) -> int:
        return self._r

    @r.setter
    def r(self, value: int):
        Color.rgb_check(value)
        self._r = value

    @property
    def g(self) -> int:
        return self._g

    @g.setter
    def g(self, value: int):
        Color.rgb_check(value)
        self._g = value

    @property
    def b(self) -> int:
        return self._b

    @b.setter
    def b(self, value: int):
        Color.rgb_check(value)
        self._b = value

    def hex(self) -> str:
        return self.repr

    @property
    def repr(self) -> str:
        return f'#{self._r:02x}{self._g:02x}{self._b:02x}'


class Card(_Common):
    _type = 'card'
    color: Optional[Color]
    modules: List[Module]

    def __init__(self, modules: List[Module] = (),
                 *,
                 color: Union[Color, Tuple[int, int, int], str, None] = None,
                 theme: Union[ThemeTypes, str] = None,
                 size: Union[SizeTypes, str] = SizeTypes.LG):
        self.modules = list(modules)

        if isinstance(color, Color):
            self.color = color
        elif isinstance(color, tuple):
            self.color = Color(color)
        elif isinstance(color, str):
            self.color = Color(hex=color)
        else:
            self.color = None

        if isinstance(theme, str):
            theme = ThemeTypes(theme)
        if isinstance(size, str):
            size = SizeTypes(size)
        super().__init__(theme, size)

    def append_module(self, module: Module):
        self.modules.append(module)

    def pop_module(self, index: int = None) -> Module:
        return self.modules.pop(index)

    @property
    def repr(self) -> Dict:
        return self._gen_dict(['type', 'theme', 'size', 'color', 'modules'])
