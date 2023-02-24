import re
import datetime
from typing import Union, Dict, List

from .struct import Struct
from .element import Element
from .interface import Types, _Module

_RE_INVITE_CODE = re.compile(r'^[a-zA-Z0-9]{6}$')
_RE_INVITE_LINK = re.compile(r'^https://kaihei\.co/[a-zA-Z0-9]{6}$')


class Module:
    """docs: https://github.com/kaiheila/api-docs/blob/main/docs/zh-cn/cardmessage.md#%E6%A8%A1%E5%9D%97"""

    class Header(_Module):
        """please refer to module docs"""
        _type = 'header'
        _text: Element.Text

        def __init__(self, text: Union[Element.Text, str] = ''):
            if isinstance(text, str):
                text = Element.Text(text)
            # Force header to use plain because KOOK right now only supports using plain in header
            self._text = Element.Text(text.content, Types.Text.PLAIN, text.emoji)
            super().__init__(Types.Theme.NA, Types.Size.NA)

        @property
        def text(self) -> Element.Text:
            """contained text"""
            return self._text

        @text.setter
        def text(self, value: Union[Element.Text, str]):
            self._text = Element.Text(value) if isinstance(value, str) else value

        @property
        def _repr(self) -> Union[Dict, str]:
            return self._gen_dict(['type', 'text'])

    class Section(_Module):
        """docs: https://t.ly/uM4K"""
        _type = 'section'
        _text: Element.Text
        _accessory: Union[Element.Image, Element.Button, None]
        mode: Types.SectionMode

        def __init__(self,
                     text: Union[Element.Text, str, Struct.Paragraph] = '',
                     accessory: Union[Element.Image, Element.Button, None] = None,
                     mode: Union[Types.SectionMode, str] = Types.SectionMode.LEFT):
            if isinstance(text, str):
                text = Element.Text(text)
            self.text = text
            self.mode = mode
            self.accessory = accessory
            super().__init__(Types.Theme.NA, Types.Size.NA)

        @property
        def text(self) -> Element.Text:
            """contained text"""
            return self._text

        @text.setter
        def text(self, value: Union[Element.Text, str]):
            self._text = Element.Text(value) if isinstance(value, str) else value

        @property
        def mode(self) -> Types.SectionMode:
            """the section's mode, refet to SectionMode for enum detail"""
            return self._mode

        @mode.setter
        def mode(self, value: Union[Types.SectionMode, str]):
            self._mode = Types.SectionMode(value) if isinstance(value, str) else value

        @property
        def accessory(self) -> Union[Element.Image, Element.Button]:
            """the accessory attached to the section, a button/an image"""
            return self._accessory

        @accessory.setter
        def accessory(self, value: Union[Element.Image, Element.Button]):
            if isinstance(value, Element.Button):
                self.mode = Types.SectionMode.RIGHT
            self._accessory = value

        @property
        def _repr(self) -> Union[Dict, str]:
            return self._gen_dict(['type', 'text', 'mode', 'accessory'])

    class ImageGroup(_Module):
        """docs: https://t.ly/2yaa"""
        _type = 'image-group'
        _elements: List[Element.Image]

        def __init__(self, *images: Element.Image):
            if not 1 <= len(images) <= 9:
                raise ValueError('element length unacceptable, should: 9 >= len >= 1')
            self._elements = list(images)
            super().__init__(Types.Theme.NA, Types.Size.NA)

        def append(self, image: Element.Image):
            """append a image into"""
            if len(self._elements) >= 9:
                raise ValueError('element max length exceeded(9)')
            self._elements.append(image)

        def pop(self, index: int = ...):
            """pop a image from"""
            if len(self._elements) <= 1:
                raise ValueError('element min length exceeded(1)')
            return self._elements.pop(index)

        def len(self) -> int:
            """count of current elements"""
            return len(self._elements)

        @property
        def _repr(self) -> Union[Dict, str]:
            return self._gen_dict(['type', 'elements'])

    class ActionGroup(_Module):
        """a group of buttons(now only support buttons)

        docs: https://t.ly/LBVJ"""
        _type = 'action-group'
        _elements: List[Element.Button]

        def __init__(self, *elements: Element.Button):
            self._elements = list(elements)
            super().__init__(Types.Theme.NA, Types.Size.NA)

        def append(self, element: Element.Button):
            """append a button into"""
            self._elements.append(element)

        def pop(self, index: int = None) -> Element.Button:
            """pop a button from"""
            return self._elements.pop(index)

        @property
        def _repr(self) -> Dict:
            return self._gen_dict(['type', 'elements'])

    class Context(_Module):
        """a set of text/images

        docs: https://t.ly/_ECm"""
        _type = 'context'
        _elements: List[Union[Element.Text, Element.Image]]

        def __init__(self, *elements: Union[Element.Text, Element.Image, str]):
            self._elements = [Element.Text(i) if isinstance(i, str) else i for i in elements]
            super().__init__(Types.Theme.NA, Types.Size.NA)

        def append(self, element: Union[Element.Text, Element.Image, str]):
            """append a text/image into"""
            self._elements.append(Element.Text(element) if isinstance(element, str) else element)

        def pop(self, index: int = None):
            """pop a text/image from"""
            return self._elements.pop(index)

        @property
        def _repr(self) -> Dict:
            return self._gen_dict(['type', 'elements'])

    class Divider(_Module):
        """docs: https://t.ly/vpuy"""
        _type = 'divider'

        def __init__(self):
            super().__init__(Types.Theme.NA, Types.Size.NA)

        @property
        def _repr(self) -> Dict:
            return {'type': 'divider'}

    class Invite(_Module):
        """component to invite others to a server

        docs: https://t.ly/q-5V"""
        _type = 'invite'

        def __init__(self, code: str = ''):
            if _RE_INVITE_CODE.match(code) or _RE_INVITE_LINK.match(code):
                self._code = code
            else:
                raise ValueError('invite code or invite link is not valid')
            super().__init__(Types.Theme.NA, Types.Size.NA)

        @property
        def code(self) -> str:
            """invite code"""
            return self._code

        @code.setter
        def code(self, value: str):
            if _RE_INVITE_CODE.match(value) or _RE_INVITE_LINK.match(value):
                self._code = value
            else:
                raise ValueError('invite code or invite link is not valid')

        @property
        def _repr(self) -> Dict:
            return self._gen_dict(['type', 'code'])

    class File(_Module):
        """show file in a module

        docs: https://t.ly/U9tm"""
        src: str
        title: str
        cover: str

        def __init__(self, type: Union[Types.File, str], src: str, title: str = '', cover: str = ''):
            self._type = type.value if isinstance(type, Types.File) else type
            self.src = src
            self.title = title
            self.cover = cover
            super().__init__(Types.Theme.NA, Types.Size.NA)

        @property
        def _repr(self) -> Dict:
            d = self._gen_dict(['type', 'src', 'title'])
            if self._type == Types.File.AUDIO.value and self.cover:
                d['cover'] = self.cover
            return d

    class Countdown(_Module):
        """count down module

        docs: https://t.ly/Xwtp"""
        _type = "countdown"
        end: datetime.datetime
        mode: Types.CountdownMode
        start: datetime.datetime

        def __init__(self,
                     end: datetime.datetime,
                     *,
                     mode: Union[Types.CountdownMode, str] = Types.CountdownMode.HOUR,
                     start: datetime.datetime = None):
            self.end = end
            self.mode = mode if isinstance(mode, Types.CountdownMode) else Types.CountdownMode(mode)
            self.start = start
            super().__init__(Types.Theme.NA, Types.Size.NA)

        @property
        def _repr(self) -> Dict:
            d = self._gen_dict(['type', 'mode'])
            if self.mode == Types.CountdownMode.SECOND and self.start:
                d['startTime'] = int(self.start.timestamp() * 1000)
            d['endTime'] = int(self.end.timestamp() * 1000)
            return d

    class Container(ImageGroup):
        """contains images, like image-group but the images are not stripped into square

        docs: https://t.ly/Rpn6"""
        _type = 'container'
