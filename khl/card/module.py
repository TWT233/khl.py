import datetime
from abc import ABC
from typing import Union, Dict, List

from .element import ImageElement, ButtonElement, TextElement
from .interface import CountdownModeTypes, FileTypes, TextTypes, SectionModeTypes, SizeTypes, ThemeTypes, _Common


class Module(_Common, ABC):
    ...


class HeaderModule(Module):
    _type = 'header'
    _text: TextElement

    def __init__(self, text: Union[TextElement, str] = ''):
        self._text = text
        super().__init__(ThemeTypes.NA, SizeTypes.NA)

    @property
    def text(self) -> TextElement:
        return self._text

    @text.setter
    def text(self, value: Union[TextElement, str]):
        self._text = value if isinstance(value, TextElement) else TextElement(TextTypes.PLAIN, value)

    @property
    def repr(self) -> Union[Dict, str]:
        return self._gen_dict(['type', 'text'])


class SectionModule(Module):
    _type = 'section'
    text: TextElement
    _accessory: Union[ImageElement, ButtonElement, None]
    mode: SectionModeTypes

    def __init__(self, text: Union[TextElement, str] = '',
                 accessory: Union[ImageElement, ButtonElement, None] = None,
                 mode: Union[SectionModeTypes, str] = SectionModeTypes.LEFT):
        self.text = text
        self.mode = mode
        self.accessory = accessory
        super().__init__(ThemeTypes.NA, SizeTypes.NA)

    @property
    def text(self) -> TextElement:
        return self._text

    @text.setter
    def text(self, value: Union[TextElement, str]):
        self._text = value if isinstance(value, TextElement) else TextElement(TextTypes.PLAIN, value)

    @property
    def mode(self) -> SectionModeTypes:
        return self._mode

    @mode.setter
    def mode(self, value: Union[SectionModeTypes, str]):
        self._mode = value if isinstance(value, SectionModeTypes) else SectionModeTypes(value)

    @property
    def accessory(self) -> Union[ImageElement, ButtonElement]:
        return self._accessory

    @accessory.setter
    def accessory(self, value: Union[ImageElement, ButtonElement]):
        if isinstance(value, ButtonElement):
            self.mode = SectionModeTypes.RIGHT
        self._accessory = value

    @property
    def repr(self) -> Union[Dict, str]:
        return self._gen_dict(['type', 'text', 'mode', 'accessory'])


class ImageGroupModule(Module):
    _type = 'image-group'
    _elements: List[ImageElement]

    def __init__(self, images: List[ImageElement]):
        if not 1 <= len(images) <= 9:
            raise ValueError('element length unacceptable, should: 9 >= len >= 1')
        self._elements = images
        super().__init__(ThemeTypes.NA, SizeTypes.NA)

    @property
    def element(self) -> List[ImageElement]:
        return self._elements

    def add_image(self, image: ImageElement):
        if len(self._elements) >= 9:
            raise ValueError('element max length exceeded(9)')
        self._elements.append(image)

    def images_count(self) -> int:
        return len(self._elements)

    def remove_image(self, n: int):
        if len(self._elements) <= 1:
            raise ValueError('element min length exceeded(1)')
        if n < 0 or n >= len(self._elements):
            return
        self._elements.pop(n)

    @property
    def repr(self) -> Union[Dict, str]:
        return self._gen_dict(['type', 'elements'])


class ActionGroupModule(Module):
    _type = 'action-group'
    _elements: List[ButtonElement]

    def __init__(self, elements: List[ButtonElement] = ()):
        self._elements = list(elements)
        super().__init__(ThemeTypes.NA, SizeTypes.NA)

    @property
    def element(self) -> List[ButtonElement]:
        return self._elements

    def append(self, element: ButtonElement):
        self._elements.append(element)

    def pop(self, index: int = None):
        return self._elements.pop(index)

    @property
    def repr(self) -> Dict:
        return self._gen_dict(['type', 'elements'])


class ContextModule(Module):
    _type = 'context'
    _elements: List[Union[TextElement, ImageElement]]

    def __init__(self, elements: List[Union[TextElement, ImageElement, str]] = ()):
        self._elements = [TextElement(TextTypes.PLAIN, i) if isinstance(i, str) else i for i in elements]
        super().__init__(ThemeTypes.NA, SizeTypes.NA)

    @property
    def element(self) -> List[Union[TextElement, ImageElement]]:
        return self._elements

    def append_element(self, element: Union[TextElement, ImageElement, str]):
        self._elements.append(TextElement(TextTypes.PLAIN, element) if isinstance(element, str) else element)

    def pop_element(self, index: int = None):
        return self._elements.pop(index)

    @property
    def repr(self) -> Dict:
        return self._gen_dict(['type', 'elements'])


class DividerModule(Module):
    _type = 'divider'

    @property
    def repr(self) -> Dict:
        return {'type': 'divider'}


class FileModule(Module):
    src: str
    title: str
    cover: str

    def __init__(self, type: Union[FileTypes, str], src: str, title: str = '', cover: str = ''):
        if isinstance(type, str):
            type = FileTypes(type)  # check if type in FileTypes
        self._type = type.value
        self.src = src
        self.title = title
        self.cover = cover
        super().__init__(ThemeTypes.NA, SizeTypes.NA)

    @property
    def repr(self) -> Dict:
        d = self._gen_dict(['type', 'src', 'title'])
        if self.type == FileTypes.AUDIO.value and self.cover:
            d['cover'] = self.cover
        return d


class CountdownModule(Module):
    _type = "countdown"
    end: datetime.datetime
    mode: CountdownModeTypes
    start: datetime.datetime

    def __init__(self, end: datetime.datetime, *,
                 mode: Union[CountdownModeTypes, str] = CountdownModeTypes.HOUR,
                 start: datetime.datetime = None):
        self.end = end
        self.mode = mode if isinstance(mode, CountdownModeTypes) else CountdownModeTypes(mode)
        self.start = start
        super().__init__(ThemeTypes.NA, SizeTypes.NA)

    @property
    def repr(self) -> Dict:
        d = self._gen_dict(['type', 'mode'])
        if self.type == CountdownModeTypes.SECOND.value and self.start:
            d['startTime'] = int(self.start.timestamp() * 1000)
        d['endTime'] = int(self.end.timestamp() * 1000)
        return d
