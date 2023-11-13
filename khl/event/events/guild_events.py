# pylint: skip-file
from typing import List

from .event import AbstractEvent


class AbstractGuildEvent(AbstractEvent):
    def __init__(self, raw: dict):
        super().__init__(raw)
        self.id: str = raw.get('id')
        self.name: str = raw.get('name')
        self.user_id: str = raw.get('user_id')
        self.icon: str = raw.get('icon')
        self.notify_type: int = raw.get('notify_type')
        self.region: str = raw.get('region')
        self.enable_open: int = raw.get('enable_open')
        self.open_id: int = raw.get('open_id')
        self.default_channel_id: str = raw.get('default_channel_id')
        self.welcome_channel_id: str = raw.get('welcome_channel_id')


class UpdateGuildEvent(AbstractGuildEvent):
    pass


class DeleteGuildEvent(AbstractGuildEvent):
    pass


class AbstractBlockListEvent(AbstractEvent):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.operator_id: str = raw.get('operator_id')
        self.user_id: List[str] = raw.get('user_id')


class AddedBlockListEvent(AbstractBlockListEvent):
    def __init__(self, raw: dict):
        super().__init__(raw)
        self.remark: str = raw.get('remark')


class DeleteBlockListEvent(AbstractBlockListEvent):
    pass


class AbstractEmojiEvent(AbstractEvent):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.id: str = raw.get('id')
        self.name: str = raw.get('name')


class AddedEmojiEvent(AbstractEmojiEvent):
    pass


class DeletedEmojiEvent(AbstractEmojiEvent):
    pass


class UpdateEmojiEvent(AbstractEmojiEvent):
    pass
