from abc import ABC
from typing import Union, Dict

from .interface import ClickTypes, TextTypes, ThemeTypes, SizeTypes, _Common


class Element(_Common, ABC):
    pass


class TextElement(Element):
    content: str
    emoji: bool

    def __init__(self, type: Union[TextTypes, str], content: str, emoji: bool = True):
        if isinstance(type, str):
            type = TextTypes(type)  # check if type in FileTypes
        self._type = type.value
        self.content = content
        self.emoji = emoji
        super().__init__(ThemeTypes.NA, SizeTypes.NA)

    @property
    def repr(self) -> Union[Dict, str]:
        if self.type == TextTypes.PLAIN.value and self.emoji:  # 「为了方便书写，所有plain-text的使用处可以简单的用字符串代替。」
            return self.content
        d = self._gen_dict(['type', 'content'])
        if self.type == TextTypes.PLAIN.value:
            d['emoji'] = self.emoji
        return d


class ImageElement(Element):
    _type = 'image'
    src: str
    alt: str
    circle: bool

    def __init__(self, src: str, alt: str, circle: bool = False, size: Union[SizeTypes, str] = SizeTypes.LG):
        self.src = src
        self.alt = alt
        self.circle = circle
        if isinstance(size, str):
            size = SizeTypes(size)
        super().__init__(ThemeTypes.NA, size)

    @property
    def repr(self) -> Dict:
        return self._gen_dict(['type', 'src', 'alt', 'size', 'circle'])


class ButtonElement(Element):
    _type = 'button'
    _click: ClickTypes
    value: str

    def __init__(self, text: str, click: Union[ClickTypes, str], value: str, theme: Union[ThemeTypes, str] = None):
        self.text = text
        self._click = click if isinstance(click, ClickTypes) else ClickTypes(click)
        self.value = value
        if isinstance(theme, str):
            theme = ThemeTypes(theme)
        super().__init__(theme, SizeTypes.NA)

    @property
    def click(self) -> str:
        return self._click.value

    @click.setter
    def click(self, value: Union[ClickTypes, str]):
        self._click = value if isinstance(value, ClickTypes) else ClickTypes(value)

    @property
    def repr(self) -> Union[Dict, str]:
        return self._gen_dict(['type', 'value', 'click', 'text'])
