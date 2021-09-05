import json
from abc import ABC
from enum import IntEnum, Enum
from typing import Any, List, Dict, Union

import api
from .channel import PublicTextChannel, PrivateChannel
from .context import Context
from .gateway import Requestable
from .guild import Guild
from .user import User


class RawMessage(ABC):
    """
    Basic and common features of kinds of messages.

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

    class ChannelTypes(Enum):
        """
        types of channel
        """
        GROUP = 'GROUP'
        PERSON = 'PERSON'

    _type: int
    _channel_type: str
    target_id: str
    author_id: str
    content: str
    msg_id: str
    msg_timestamp: int
    nonce: str
    extra: Any

    def __init__(self, **kwargs):
        self._type = kwargs.get('type')
        self._channel_type = kwargs.get('channel_type')
        self.target_id = kwargs.get('target_id')
        self.author_id = kwargs.get('author_id')
        self.content = kwargs.get('content')
        self.msg_id = kwargs.get('msg_id')
        self.msg_timestamp = kwargs.get('msg_timestamp')
        self.nonce = kwargs.get('nonce')
        self.extra = kwargs.get('extra', {})

    @property
    def type(self) -> Types:
        return RawMessage.Types(self._type)

    @property
    def channel_type(self) -> ChannelTypes:
        return RawMessage.ChannelTypes(self._channel_type)


class Message(RawMessage, Requestable, ABC):
    """
    Represents the messages sent by user.

    Because it has source and context, we can interact with its sender and context via it.

    now there are two types of message:
        1. ChannelMessage: sent in a guild channel
        2. PrivateMessage: sent in a private chat
    """
    _ctx: Context

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gate = kwargs.get('_gate_', None)
        self._author = User(**self.extra['author'], _gate_=self.gate, _lazy_loaded_=True)

    @property
    def author(self) -> User:
        return self._author

    @property
    def ctx(self) -> Context:
        return self._ctx

    async def reply(self, content: Union[str, List] = '', use_quote: bool = True, **kwargs):
        """
        reply to a msg, content can also be a card
        """

        if isinstance(content, List):
            kwargs['type'] = RawMessage.Types.CARD.value
            content = json.dumps(content)
        if use_quote:
            kwargs['quote'] = self.msg_id

        if self.channel_type == RawMessage.ChannelTypes.PERSON:
            req = api.DirectMessage.create(target_id=self.author.id, content=content, **kwargs)
        elif self.channel_type == RawMessage.ChannelTypes.GROUP:
            req = api.Message.create(target_id=self.ctx.channel.id, content=content, **kwargs)
        else:
            raise ValueError(f"Unacceptable channel_type: {self.channel_type}")

        return await self.gate.requester.exec_req(req)


class PublicMessage(Message):
    """
    Messages sent in a `PublicTextChannel`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._channel = PublicTextChannel(id=self.target_id, name=self.extra['channel_name'])
        self._ctx = Context(channel=self._channel, guild=Guild(id=self.extra['guild_id']), _gate_=self.gate)

    @property
    def guild(self) -> Guild:
        return self._ctx.guild

    @property
    def channel(self) -> PublicTextChannel:
        return self._channel

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

    async def reply(self, content: Union[str, List] = '', use_quote: bool = True, temp_target_id: str = '', **kwargs):
        return await super().reply(content, use_quote, temp_target_id=temp_target_id, **kwargs)


class PrivateMessage(Message):
    """
    Messages sent in a `PrivateChannel`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._channel = PrivateChannel(code=self.extra['code'], target_info=self.extra['author'])
        self._ctx = Context(channel=self._channel, _gate_=self.gate)

    @property
    def chat_code(self) -> str:
        return self.extra['code']

    @property
    def channel(self) -> PrivateChannel:
        return self._channel


class Event(RawMessage):
    @property
    def event_type(self) -> str:
        return self.extra['type']

    @property
    def body(self) -> Dict:
        return self.extra['body']
