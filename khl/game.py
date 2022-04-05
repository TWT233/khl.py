from typing import List


class Game:
    id: int
    name: str
    type: int
    options: str
    kmhook_admin: bool
    process_name: List[str]
    product_name: List[str]
    icon: str

    def __init__(self, **kwargs) -> None:
        self.id = kwargs.get('id', '')
        self.name = kwargs.get('name', '')
        self.type = kwargs.get('type', 1)
        self.options = kwargs.get('options', [])
        self.product_name = kwargs.get('product_name', [])
        self.icon = kwargs.get('icon', '')
