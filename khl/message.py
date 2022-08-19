from abc import ABC, abstractmethod
from typing import Any, List, Dict, Union

from . import api
from .channel import PublicTextChannel, PrivateChannel
from .context import Context
from .gateway import Requestable
from .guild import Guild
from ._types import MessageTypes, ChannelPrivacyTypes, EventTypes
from .user import User


class RawMessage(ABC):
    """
    Basic and common features of kinds of messages.

    now support Message kinds:
        1. Message (sent by users, those normal chats such as TEXT/IMG etc.)
        2. Event (sent by system, such as notifications and broadcasts)
    """

    _type: int
    _channel_type: str
    target_id: str
    author_id: str
    content: str
    _msg_id: str
    msg_timestamp: int
    nonce: str
    extra: Any

    def __init__(self, **kwargs):
        self._msg_id = kwargs.get('msg_id')
        self._type = kwargs.get('type')
        self._channel_type = kwargs.get('channel_type')
        self.target_id = kwargs.get('target_id')
        self.author_id = kwargs.get('author_id')
        self.content = kwargs.get('content')
        self.msg_timestamp = kwargs.get('msg_timestamp')
        self.nonce = kwargs.get('nonce')
        self.extra = kwargs.get('extra', {})

    @property
    def id(self) -> str:
        """message's id"""
        return self._msg_id

    @property
    def type(self) -> MessageTypes:
        """message's type, refer to MessageTypes for enum detail"""
        return MessageTypes(self._type)

    @property
    def channel_type(self) -> ChannelPrivacyTypes:
        """type of the channel where the message in"""
        return ChannelPrivacyTypes(self._channel_type)


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
        """message author"""
        return self._author

    @property
    def ctx(self) -> Context:
        """message context: channel, guild etc."""
        return self._ctx

    @abstractmethod
    async def add_reaction(self, emoji: str):
        """add emoji to msg's reaction list

        https://developer.kaiheila.cn/doc/http/message#%E7%BB%99%E6%9F%90%E4%B8%AA%E6%B6%88%E6%81%AF%E6%B7%BB%E5%8A%A0%E5%9B%9E%E5%BA%94

        https://developer.kaiheila.cn/doc/http/direct-message#%E7%BB%99%E6%9F%90%E4%B8%AA%E6%B6%88%E6%81%AF%E6%B7%BB%E5%8A%A0%E5%9B%9E%E5%BA%94

        :param emoji: 😘
        """

    @abstractmethod
    async def delete_reaction(self, emoji: str, user: User):
        """delete emoji from msg's reaction list

        https://developer.kaiheila.cn/doc/http/message#%E5%88%A0%E9%99%A4%E6%B6%88%E6%81%AF%E7%9A%84%E6%9F%90%E4%B8%AA%E5%9B%9E%E5%BA%94

        https://developer.kaiheila.cn/doc/http/direct-message#%E5%88%A0%E9%99%A4%E6%B6%88%E6%81%AF%E7%9A%84%E6%9F%90%E4%B8%AA%E5%9B%9E%E5%BA%94

        :param emoji: 😘
        :param user: whose reaction, delete others added reaction requires channel msg admin permission
        """

    async def reply(self,
                    content: Union[str, List] = '',
                    use_quote: bool = True,
                    *,
                    type: MessageTypes = None,
                    **kwargs):
        """
        reply to a msg, content can also be a card
        """
        if use_quote:
            kwargs['quote'] = self.id

        return await self.ctx.channel.send(content, type=type, **kwargs)

    async def delete(self):
        """delete the message, permission required"""
        return await self.gate.exec_req(api.Message.delete(msg_id=self.id))


class PublicMessage(Message):
    """
    Messages sent in a `PublicTextChannel`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        channel = PublicTextChannel(id=self.target_id, name=self.extra['channel_name'], _gate_=self.gate)
        guild = Guild(id=self.extra['guild_id'], _gate_=self.gate)
        self._ctx = Context(channel=channel, guild=guild, _gate_=self.gate)

    @property
    def guild(self) -> Guild:
        """the guild where the message in"""
        return self.ctx.guild

    @property
    def channel(self) -> PublicTextChannel:
        """the channel where the message in"""
        if isinstance(self.ctx.channel, PublicTextChannel):
            return self.ctx.channel
        raise ValueError('PublicMessage should be placed in PublicTextChannel')

    @property
    def mention(self) -> List[str]:
        """the message mentioned(also call as at/tagged) users' id"""
        return self.extra['mention']

    @property
    def mention_all(self) -> bool:
        """if the message mentioned(also call as at/tagged) all"""
        return self.extra['mention_all']

    @property
    def mention_roles(self) -> List:
        """the message mentioned(also call as at/tagged) roles' id"""
        return self.extra['mention_roles']

    @property
    def mention_here(self) -> bool:
        """if the message mentioned(also call as at/tagged) all online users in the channel"""
        return self.extra['mention_here']

    async def add_reaction(self, emoji: str):
        return await self.gate.exec_req(api.Message.addReaction(msg_id=self.id, emoji=emoji))

    async def delete_reaction(self, emoji: str, user: User = None):
        req = api.Message.deleteReaction(msg_id=self.id, emoji=emoji, user_id=user.id if user else '')
        return await self.gate.exec_req(req)

    async def reply(self,
                    content: Union[str, List] = '',
                    use_quote: bool = True,
                    is_temp: bool = False,
                    *,
                    type: MessageTypes = None,
                    **kwargs):
        return await super().reply(content,
                                   use_quote,
                                   temp_target_id=self.author_id if is_temp else '',
                                   type=type,
                                   **kwargs)


class PrivateMessage(Message):
    """
    Messages sent in a `PrivateChannel`
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._channel = PrivateChannel(code=self.extra['code'], target_info=self.extra['author'], _gate_=self.gate)
        self._ctx = Context(channel=self._channel, _gate_=self.gate)

    @property
    def chat_code(self) -> str:
        """the chat code of this private chat"""
        return self.extra['code']

    @property
    def channel(self) -> PrivateChannel:
        """the message's channel"""
        return self._channel

    async def add_reaction(self, emoji: str):
        return await self.gate.exec_req(api.DirectMessage.addReaction(msg_id=self.id, emoji=emoji))

    async def delete_reaction(self, emoji: str, user: User = None):
        req = api.DirectMessage.deleteReaction(msg_id=self.id, emoji=emoji, user_id=user.id if user else '')
        return await self.gate.exec_req(req)


class Event(RawMessage):
    """sent by system, opposites to Message, carries various types of payload"""

    @property
    def event_type(self) -> EventTypes:
        """type of the event, refer to EventTypes for enum detail"""
        return EventTypes(self.extra['type'])

    @property
    def body(self) -> Dict:
        """event body, a dict, refer to official docs with the event_type for the actual struct

        docs: https://developer.kaiheila.cn/doc/event/event-introduction"""
        return self.extra['body']
