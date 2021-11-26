
from typing import Union, Dict, List
from .element import TextElement
from .module import (Module,ContextModule)
from .interface import ThemeTypes,SizeTypes

class ParagraphStruct(Module):
    _type = 'paragraph'
    cols: int
    _fields: List[Union[TextElement, ContextModule]]

    def __init__(self, cols: int, fields: List[Union[TextElement, ContextModule]]):
        if not 1 <= cols <= 3:
            raise ValueError('cols length unacceptable, should: 3 >= len >= 1')
        self._fields = fields
        self.cols = cols
        super().__init__(ThemeTypes.NA, SizeTypes.NA)

    @property
    def fields(self) -> List[Union[TextElement, ContextModule]]:
        return self._fields

    def add_field(self, field: Union[TextElement, ContextModule]):
        self._fields.append(field)

    def fields_count(self) -> int:
        return len(self._fields)

    def remove_field(self, n: int):
        if n < 0 or n >= len(self._fields):
            return
        self._fields.pop(n)

    @property
    def fields(self) -> List[Union[TextElement, ContextModule]]:
        return self._fields

    @property
    def repr(self) -> Union[Dict, str]:
        return self._gen_dict(['type', 'cols', 'fields'])
