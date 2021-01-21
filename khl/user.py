from typing import Any, Mapping


class User:
    """
    presents a User in chat/group

    including other bots
    """
    def __init__(self, data: Mapping[str, Any]):
        self.id: str = data['id']
        pass
