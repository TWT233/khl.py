import json
from abc import ABC, abstractmethod
from typing import Union, List, overload, Dict

from . import api
from .gateway import Requestable, Gateway
from .interface import LazyLoadable, MessageTypes, ChannelTypes


class Channel(LazyLoadable, Requestable, ABC):
    """
    Interface, represents a channel where messages flowing
    """
    type: ChannelTypes

    @abstractmethod
    async def send(self, content: Union[str, List], **kwargs):
        """
        send a msg to the channel
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError


class PublicChannel(Channel, ABC):
    name: str
    user_id: str
    guild_id: str
    topic: str
    is_category: int
    parent_id: str
    level: int
    permission_overwrites: list
    permission_users: list
    permission_sync: int

    def __init__(self, **kwargs):
        self._id: str = kwargs.get('id')
        self._loaded = kwargs.get('_lazy_loaded_', False)
        self.gate = kwargs.get('_gate_')
        self._update_fields(**kwargs)

    @property
    def id(self) -> str:
        return self._id

    def _update_fields(self, **kwargs):
        self.name: str = kwargs.get('name')
        self.user_id: str = kwargs.get('user_id')
        self.guild_id: str = kwargs.get('guild_id')
        self.topic: str = kwargs.get('topic')
        self.is_category: int = kwargs.get('is_category')
        self.parent_id: str = kwargs.get('parent_id')
        self.level: int = kwargs.get('level')
        self.type: ChannelTypes = kwargs.get('type') and ChannelTypes(kwargs.get('type'))
        self.permission_overwrites: list = kwargs.get('permission_overwrites')
        self.permission_users: list = kwargs.get('permission_users')
        self.permission_sync: int = kwargs.get('permission_sync')

    async def load(self):
        self._update_fields(**(await self.gate.exec_req(api.Channel.view(self.id))))
        self._loaded = True


class PublicTextChannel(PublicChannel):
    """
    `Standard Object`

    Text chat channels in guild
    """
    slow_mode: int

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _update_fields(self, **kwargs):
        super()._update_fields(**kwargs)
        self.slow_mode: int = kwargs.get('slow_mode')

    @overload
    async def send(self, content: Union[str, List], **kwargs):
        ...

    async def send(self, content: Union[str, List], *, temp_target_id: str = '', **kwargs):
        """
        send a msg to the channel

        ``temp_target_id`` is available in PublicTextChannel, so ``send()`` is overloaded here
        """
        # if content is card msg, then convert it to plain str
        if isinstance(content, List):
            kwargs['type'] = MessageTypes.CARD
            content = json.dumps(content)
        if 'type' not in kwargs:
            kwargs['type'] = MessageTypes.TEXT

        # merge params
        kwargs['target_id'] = self.id
        kwargs['content'] = content
        if isinstance(kwargs['type'], MessageTypes):
            kwargs['type'] = kwargs['type'].value
        if temp_target_id:
            kwargs['temp_target_id'] = temp_target_id

        return await self.gate.exec_req(api.Message.create(**kwargs))


class PublicVoiceChannel(PublicChannel):
    """
    Voice chat channel in guild

    a placeholder now for future design/adaption
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def send(self, content: Union[str, List], **kwargs):
        raise TypeError('now there is no PublicVoiceChannel, *hey dude we have a pkg from future*')


def public_channel_factory(_gate_: Gateway, **kwargs) -> PublicChannel:
    kwargs['type'] = kwargs['type'] if isinstance(kwargs['type'], ChannelTypes) else ChannelTypes(kwargs['type'])
    if kwargs['type'] == ChannelTypes.TEXT:
        return PublicTextChannel(**kwargs, _gate_=_gate_)
    elif kwargs['type'] == ChannelTypes.VOICE:
        return PublicVoiceChannel(**kwargs, _gate_=_gate_)


class PrivateChannel(Channel):
    """
    Private chat channel
    """

    code: str
    last_read_time: int
    latest_msg_time: int
    unread_count: int
    is_friend: bool
    is_blocked: bool
    is_target_blocked: bool
    target_info: Dict

    def __init__(self, **kwargs):
        self.code: str = kwargs.get('code')
        self.last_read_time: int = kwargs.get('last_read_time')
        self.latest_msg_time: int = kwargs.get('latest_msg_time')
        self.unread_count: int = kwargs.get('unread_count')
        self.is_friend: bool = kwargs.get('is_friend')
        self.is_blocked: bool = kwargs.get('is_blocked')
        self.is_target_blocked: bool = kwargs.get('is_target_blocked')
        self.target_info: Dict = kwargs.get('target_info')

        self._loaded = kwargs.get('_lazy_loaded_', False)
        self.gate = kwargs.get('_gate_')

    async def load(self):
        pass

    @property
    def id(self) -> str:
        return self.target_user_id

    @property
    def target_user_id(self) -> str:
        return self.target_info.get('id') if self.target_info else None

    @property
    def target_user_name(self) -> str:
        return self.target_info.get('username') if self.target_info else None

    @property
    def is_target_user_online(self) -> bool:
        return self.target_info.get('online') if self.target_info else None

    @property
    def target_user_avatar(self) -> str:
        return self.target_info.get('avatar') if self.target_info else None

    async def send(self, content: Union[str, List], **kwargs):
        # if content is card msg, then convert it to plain str
        if isinstance(content, List):
            kwargs['type'] = MessageTypes.CARD.value
            content = json.dumps(content)
        if 'type' not in kwargs:
            kwargs['type'] = MessageTypes.TEXT

        # merge params
        if self.code:
            kwargs['chat_code'] = self.code
        else:
            kwargs['target_id'] = self.target_user_id
        kwargs['content'] = content
        if isinstance(kwargs['type'], MessageTypes):
            kwargs['type'] = kwargs['type'].value

        return await self.gate.exec_req(api.DirectMessage.create(**kwargs))
