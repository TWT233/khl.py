from typing import Union, Dict

from .interface import Types, _Element


class Element:

    class Text(_Element):
        content: str
        emoji: bool

        def __init__(self, content: str, type: Union[Types.Text, str] = Types.Text.PLAIN, emoji: bool = True):
            if isinstance(type, str):
                type = Types.Text(type)  # check if type in Type.Text
            self._type = type.value
            self.content = content
            self.emoji = emoji
            super().__init__(Types.Theme.NA, Types.Size.NA)

        @property
        def _repr(self) -> Union[Dict, str]:
            if self._type == Types.Text.PLAIN.value and self.emoji:  # 「为了方便书写，所有plain-text的使用处可以简单的用字符串代替。」
                return self.content
            d = self._gen_dict(['type', 'content'])
            if self._type == Types.Text.PLAIN.value:
                d['emoji'] = self.emoji
            return d

    class Image(_Element):
        _type = 'image'
        src: str
        alt: str
        circle: bool

        def __init__(self, src: str, alt: str = '', circle: bool = False, size: Union[Types.Size, str] = Types.Size.LG):
            self.src = src
            self.alt = alt
            self.circle = circle
            if isinstance(size, str):
                size = Types.Size(size)
            super().__init__(Types.Theme.NA, size)

        @property
        def _repr(self) -> Dict:
            return self._gen_dict(['type', 'src', 'alt', 'size', 'circle'])

    class Button(_Element):
        _type = 'button'
        _click: Types.Click
        text: 'Element.Text'
        value: str

        def __init__(self,
                     text: Union['Element.Text', str],
                     value: str = '',
                     click: Union[Types.Click, str] = Types.Click.RETURN_VAL,
                     theme: Union[Types.Theme, str, None] = None):
            self.text = text
            self._click = click if isinstance(click, Types.Click) else Types.Click(click)
            self.value = value
            super().__init__(theme, Types.Size.NA)

        @property
        def click(self) -> str:
            return self._click.value

        @click.setter
        def click(self, value: Union[Types.Click, str]):
            self._click = value if isinstance(value, Types.Click) else Types.Click(value)

        @property
        def _repr(self) -> Union[Dict, str]:
            return self._gen_dict(['type', 'value', 'click', 'text', 'theme'])
