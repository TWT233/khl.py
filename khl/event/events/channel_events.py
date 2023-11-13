# pylint: skip-file
from abc import ABC
from typing import List

from .event import AbstractEvent


class AbstractReactionEvent(AbstractEvent, ABC):
    def __init__(self, raw: dict):
        super().__init__(raw)
        self.msg_id: str = raw.get('msg_id')
        self.user_id: str = raw.get('user_id')
        self.channel_id: str = raw.get('channel_id')
        self.emoji: dict = raw.get('emoji')


class AddedReactionEvent(AbstractReactionEvent):
    pass


class DeletedReactionEvent(AbstractReactionEvent):
    pass


class UpdatedMessageEvent(AbstractEvent):
    def __init__(self, raw: dict):
        super().__init__(raw)
        self.msg_id: str = raw.get('msg_id')
        self.content: str = raw.get('content')
        self.channel_id: str = raw.get('channel_id')
        self.mention: List[str] = raw.get('mention')
        self.mention_all: bool = raw.get('mention_all')
        self.mention_here: bool = raw.get('mention_here')
        self.mention_roles: List[int] = raw.get('mention_roles')
        self.updated_at: int = raw.get('updated_at')


class DeletedMessageEvent(AbstractEvent):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.msg_id: str = raw.get('msg_id')
        self.channel_id: str = raw.get('channel_id')


class AddedChannelEvent(AbstractEvent):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.channel: dict = raw


class DeletedChannelEvent(AbstractEvent):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.id: str = raw.get('id')
        self.deleted_at: int = raw.get('deleted_at')


class AbstractPinEvent(AbstractEvent, ABC):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.channel_id: str = raw.get('channel_id')
        self.operator_id: str = raw.get('operator_id')
        self.msg_id: str = raw.get('msg_id')


class PinnedMessageEvent(AbstractPinEvent):
    pass


class UnpinnedMessageEvent(AbstractPinEvent):
    pass
