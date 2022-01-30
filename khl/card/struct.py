from typing import Union, List, Dict

from .element import Element
from .interface import _Struct, Types


class Struct:

    class Paragraph(_Struct):
        _type = 'paragraph'
        _cols: int
        _fields: List[Element.Text]

        def __init__(self, cols: int, *fields: Union[Element.Text, str]):
            if not 1 <= len(fields) <= 50:
                raise ValueError('fields length unacceptable, should: 50 >= len >= 1')
            self._cols = cols
            self._fields = [f if isinstance(f, Element.Text) else Element.Text(f) for f in fields]
            super().__init__(Types.Theme.NA, Types.Size.NA)

        def append(self, field: Element.Text):
            if len(self._fields) >= 50:
                raise ValueError('fields max length exceeded(50)')
            self._fields.append(field)

        def pop(self, index: int) -> Element.Text:
            if len(self._fields) <= 1:
                raise ValueError('fields min length exceeded(1)')
            return self._fields.pop(index)

        def len(self):
            return len(self._fields)

        @property
        def _repr(self) -> Union[str, Dict]:
            return self._gen_dict(['type', 'cols', 'fields'])
