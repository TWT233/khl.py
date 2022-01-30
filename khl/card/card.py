from typing import List, Union, Tuple, Optional, Dict

from .color import Color, make_color
from .interface import Types, _Common
from .module import _Module


class Card(_Common):
    _type = 'card'
    _color: Optional[Color]
    _modules: List[_Module]

    def __init__(self,
                 *modules: _Module,
                 color: Union[Color, Tuple[int, int, int], str, None] = None,
                 theme: Union[Types.Theme, str, None] = None,
                 size: Union[Types.Size, str, None] = Types.Size.LG):
        self._modules = list(modules)
        self._color = make_color(color)
        super().__init__(theme, size)

    def append(self, module: _Module):
        self._modules.append(module)

    def pop(self, index: int = None) -> _Module:
        return self._modules.pop(index)

    @property
    def color(self) -> Optional[Color]:
        return self._color

    @color.setter
    def color(self, value: Union[Color, Tuple[int, int, int], str]):
        self._color = make_color(value)

    @property
    def theme(self) -> Types.Theme:
        return self._theme

    @theme.setter
    def theme(self, value: Union[Types.Theme, str]):
        self._theme = Types.Theme(value)

    @property
    def size(self) -> Types.Size:
        return self._size

    @size.setter
    def size(self, value: Union[Types.Size, str]):
        self._size = Types.Size(value)

    @property
    def _repr(self) -> Dict:
        return self._gen_dict(['type', 'theme', 'size', 'color', 'modules'])
