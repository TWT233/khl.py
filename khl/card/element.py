from typing import Union, Dict

from .interface import ClickTypes, TextTypes, ThemeTypes, SizeTypes, _Element


class Element:
    class Text(_Element):
        content: str
        emoji: bool

        def __init__(self, content: str, type: Union[TextTypes, str] = TextTypes.PLAIN, emoji: bool = True):
            if isinstance(type, str):
                type = TextTypes(type)  # check if type in TextTypes
            self._type = type.value
            self.content = content
            self.emoji = emoji
            super().__init__(ThemeTypes.NA, SizeTypes.NA)

        @property
        def _repr(self) -> Union[Dict, str]:
            if self._type == TextTypes.PLAIN.value and self.emoji:  # 「为了方便书写，所有plain-text的使用处可以简单的用字符串代替。」
                return self.content
            d = self._gen_dict(['type', 'content'])
            if self._type == TextTypes.PLAIN.value:
                d['emoji'] = self.emoji
            return d

    class Image(_Element):
        _type = 'image'
        src: str
        alt: str
        circle: bool

        def __init__(self, src: str, alt: str = '', circle: bool = False, size: Union[SizeTypes, str] = SizeTypes.LG):
            self.src = src
            self.alt = alt
            self.circle = circle
            if isinstance(size, str):
                size = SizeTypes(size)
            super().__init__(ThemeTypes.NA, size)

        @property
        def _repr(self) -> Dict:
            return self._gen_dict(['type', 'src', 'alt', 'size', 'circle'])

    class Button(_Element):
        _type = 'button'
        _click: ClickTypes
        value: str

        def __init__(self, text: str, click: Union[ClickTypes, str], value: str,
                     theme: Union[ThemeTypes, str, None] = None):
            self.text = text
            self._click = click if isinstance(click, ClickTypes) else ClickTypes(click)
            self.value = value
            super().__init__(theme, SizeTypes.NA)

        @property
        def click(self) -> str:
            return self._click.value

        @click.setter
        def click(self, value: Union[ClickTypes, str]):
            self._click = value if isinstance(value, ClickTypes) else ClickTypes(value)

        @property
        def _repr(self) -> Union[Dict, str]:
            return self._gen_dict(['type', 'value', 'click', 'text'])
