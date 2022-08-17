"""components in Element category"""
from typing import Union, Dict

from .interface import Types, _Common


class Element:
    """components in Element category

    the most basic content delivers, usually contained in module"""

    class Text(_Common):
        """Text Element"""
        content: str
        emoji: bool

        def __init__(self, content: str, text_type: Union[Types.Text, str] = Types.Text.PLAIN, emoji: bool = True):
            if isinstance(text_type, str):
                text_type = Types.Text(text_type)  # check if type in Type.Text
            self._type = text_type.value
            self.content = content
            self.emoji = emoji
            super().__init__(Types.Theme.NA, Types.Size.NA)

        @property
        def _repr(self) -> Union[Dict, str]:
            # 「为了方便书写，所有plain-text的使用处可以简单的用字符串代替。」
            if self._type == Types.Text.PLAIN.value and self.emoji:
                return self.content
            result = self._gen_dict(['type', 'content'])
            if self._type == Types.Text.PLAIN.value:
                result['emoji'] = self.emoji
            return result

    class Image(_Common):
        """Image Element"""
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

    class Button(_Common):
        """Button Element

        can react to user's click"""
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
            """there is two types of actions for button to react when user clicks, which depends on the `Button.click`:

            1. `Button.click` == Types.Click.RETURN_VAL:
            returns the `Button.value` back to bot

            2. `Button.click` == Types.Click.LINK:
            khl client will open a browser tab for user, with link = `Button.value`"""
            return self._click.value

        @click.setter
        def click(self, value: Union[Types.Click, str]):
            self._click = value if isinstance(value, Types.Click) else Types.Click(value)

        @property
        def _repr(self) -> Union[Dict, str]:
            return self._gen_dict(['type', 'value', 'click', 'text', 'theme'])
