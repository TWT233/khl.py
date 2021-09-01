from interface import ABC
from enum import IntEnum
from typing import Any, List, Dict

from .gateway import Requestable
from .channel import Channel
from .context import Context
from .guild import Guild
from .user import User


class BaseMessage(Requestable, ABC):
    """
    Base class for kinds of Message

    now support Message kinds:
        1. Message (sent by users, those normal chats such as TEXT/IMG etc.)
        2. Event (sent by system, such as notifications and broadcasts)
    """

    class Types(IntEnum):
        """
        types of message, type==SYS will be interpreted as `Event`, others are `Message`
        """
        TEXT = 1
        IMG = 2
        VIDEO = 3
        FILE = 4
        AUDIO = 8
        KMD = 9
        CARD = 10
        SYS = 255

    _type: int
    channel_type: str
    target_id: str
    author_id: str
    content: str
    msg_id: str
    msg_timestamp: int
    nonce: str
    extra: Any

    _ctx: Context

    def __init__(self, **kwargs):
        self._type = kwargs.get('type', 0)
        self.channel_type = kwargs.get('channel_type', '')
        self.target_id = kwargs.get('target_id', '')
        self.author_id = kwargs.get('author_id', '')
        self.content = kwargs.get('content', '')
        self.msg_id = kwargs.get('msg_id', '')
        self.msg_timestamp = kwargs.get('msg_timestamp', 0)
        self.nonce = kwargs.get('nonce', '')
        self.extra = kwargs.get('extra', {})

        self._gate = kwargs.get('_gate_', None)
        self._ctx = Context(channel=Channel(id=self.target_id), _gate_=self.gate)

    @property
    def type(self) -> Types:
        return BaseMessage.Types(self._type)


class Message(BaseMessage):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ctx.guild = Guild(id=self.extra['guild_id'])
        self._ctx.channel.name = self.extra['channel_name']

    @property
    def guild(self) -> Guild:
        return self._ctx.guild

    @property
    def channel(self) -> Channel:
        return self._ctx.channel

    @property
    def mention(self) -> List[str]:
        return self.extra['mention']

    @property
    def mention_all(self) -> bool:
        return self.extra['mention_all']

    @property
    def mention_roles(self) -> List:  # TODO: check type
        return self.extra['mention_roles']

    @property
    def mention_here(self) -> bool:
        return self.extra['mention_here']

    @property
    def author(self) -> User:
        return User(**self.extra['author'], _gate_=self._gate, _lazy_loaded_=True)


class Event(BaseMessage):
    @property
    def event_type(self) -> str:
        return self.extra['type']

    @property
    def body(self) -> Dict:
        return self.extra['body']
