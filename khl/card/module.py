import datetime
from typing import Union, Dict, List

from .struct import Struct
from .element import Element
from .interface import Types, _Module


class Module:

    class Header(_Module):
        _type = 'header'
        _text: Element.Text

        def __init__(self, text: Union[Element.Text, str] = ''):
            self._text = text
            super().__init__(Types.Theme.NA, Types.Size.NA)

        @property
        def text(self) -> Element.Text:
            return self._text

        @text.setter
        def text(self, value: Union[Element.Text, str]):
            self._text = Element.Text(value) if isinstance(value, str) else value

        @property
        def _repr(self) -> Union[Dict, str]:
            return self._gen_dict(['type', 'text'])

    class Section(_Module):
        _type = 'section'
        _text: Element.Text
        _accessory: Union[Element.Image, Element.Button, None]
        mode: Types.SectionMode

        def __init__(self,
                     text: Union[Element.Text, str, Struct.Paragraph] = '',
                     accessory: Union[Element.Image, Element.Button, None] = None,
                     mode: Union[Types.SectionMode, str] = Types.SectionMode.LEFT):
            self.text = text
            self.mode = mode
            self.accessory = accessory
            super().__init__(Types.Theme.NA, Types.Size.NA)

        @property
        def text(self) -> Element.Text:
            return self._text

        @text.setter
        def text(self, value: Union[Element.Text, str]):
            self._text = Element.Text(value) if isinstance(value, str) else value

        @property
        def mode(self) -> Types.SectionMode:
            return self._mode

        @mode.setter
        def mode(self, value: Union[Types.SectionMode, str]):
            self._mode = Types.SectionMode(value) if isinstance(value, str) else value

        @property
        def accessory(self) -> Union[Element.Image, Element.Button]:
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
        _type = 'image-group'
        _elements: List[Element.Image]

        def __init__(self, *images: Element.Image):
            if not 1 <= len(images) <= 9:
                raise ValueError('element length unacceptable, should: 9 >= len >= 1')
            self._elements = list(images)
            super().__init__(Types.Theme.NA, Types.Size.NA)

        def append(self, image: Element.Image):
            if len(self._elements) >= 9:
                raise ValueError('element max length exceeded(9)')
            self._elements.append(image)

        def pop(self, index: int):
            if len(self._elements) <= 1:
                raise ValueError('element min length exceeded(1)')
            return self._elements.pop(index)

        def len(self) -> int:
            return len(self._elements)

        @property
        def _repr(self) -> Union[Dict, str]:
            return self._gen_dict(['type', 'elements'])

    class ActionGroup(_Module):
        _type = 'action-group'
        _elements: List[Element.Button]

        def __init__(self, *elements: Element.Button):
            self._elements = list(elements)
            super().__init__(Types.Theme.NA, Types.Size.NA)

        def append(self, element: Element.Button):
            self._elements.append(element)

        def pop(self, index: int = None) -> Element.Button:
            return self._elements.pop(index)

        @property
        def _repr(self) -> Dict:
            return self._gen_dict(['type', 'elements'])

    class Context(_Module):
        _type = 'context'
        _elements: List[Union[Element.Text, Element.Image]]

        def __init__(self, *elements: Union[Element.Text, Element.Image, str]):
            self._elements = [Element.Text(i) if isinstance(i, str) else i for i in elements]
            super().__init__(Types.Theme.NA, Types.Size.NA)

        def append(self, element: Union[Element.Text, Element.Image, str]):
            self._elements.append(Element.Text(element) if isinstance(element, str) else element)

        def pop(self, index: int = None):
            return self._elements.pop(index)

        @property
        def _repr(self) -> Dict:
            return self._gen_dict(['type', 'elements'])

    class Divider(_Module):
        _type = 'divider'

        def __init__(self):
            super().__init__(Types.Theme.NA, Types.Size.NA)

        @property
        def _repr(self) -> Dict:
            return {'type': 'divider'}

    class File(_Module):
        src: str
        title: str
        cover: str

        def __init__(self, type: Union[Types.File, str], src: str, title: str = '', cover: str = ''):
            if isinstance(type, str):
                type = Types.File(type)  # check if type in Type.File
            self._type = type.value
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
            if self._type == Types.CountdownMode.SECOND.value and self.start:
                d['startTime'] = int(self.start.timestamp() * 1000)
            d['endTime'] = int(self.end.timestamp() * 1000)
            return d

    class Container(_Module):
        # 除_type和ImageGroup不一样 其余完全一致
        # class Container(ImageGroup):
        #     _type = 'container'
        # 偷懒一点这样也没什么问题(
        _type = 'container'
        _elements: List[Element.Image]

        def __init__(self, *images: Element.Image):
            if not 1 <= len(images) <= 9:
                raise ValueError('element length unacceptable, should: 9 >= len >= 1')
            self._elements = list(images)
            super().__init__(Types.Theme.NA, Types.Size.NA)

        def append(self, image: Element.Image):
            if len(self._elements) >= 9:
                raise ValueError('element max length exceeded(9)')
            self._elements.append(image)

        def pop(self, index: int):
            if len(self._elements) <= 1:
                raise ValueError('element min length exceeded(1)')
            return self._elements.pop(index)

        def len(self) -> int:
            return len(self._elements)

        @property
        def _repr(self) -> Union[Dict, str]:
            return self._gen_dict(['type', 'elements'])
