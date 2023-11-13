from abc import ABC

from .channel_events import AbstractReactionEvent
from .event import AbstractEvent


class AbstractPrivateMessageEvent(AbstractEvent, ABC):
    def __init__(self, raw: dict):
        super().__init__(raw)
        self.msg_id: str = raw.get('msg_id')
        self.author_id: str = raw.get('author_id')
        self.target_id: str = raw.get('target_id')
        self.chat_code: str = raw.get('chat_code')


class UpdatePrivateMessageEvent(AbstractPrivateMessageEvent):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.content: str = raw.get('content')
        self.updated_at: int = raw.get('updated_at')


class DeletedPrivateMessageEvent(AbstractPrivateMessageEvent):
    def __init__(self, raw: dict):
        super().__init__(raw)
        self.deleted_at: int = raw.get('deleted_at')


class AbstractPrivateReactionEvent(AbstractReactionEvent):

    def __init__(self, raw: dict):
        super().__init__(raw)
        self.chat_code: str = raw.get('chat_code')


class PrivateAddedReactionEvent(AbstractPrivateReactionEvent):
    pass


class PrivateDeletedReactionEvent(AbstractPrivateReactionEvent):
    pass
