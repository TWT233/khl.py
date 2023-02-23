"""abstraction of khl concept channel: where messages flow in"""
import json
from abc import ABC, abstractmethod
from typing import Union, List, Dict

from . import api
from ._types import MessageTypes, ChannelTypes, SlowModeTypes, MessageFlagModes
from .gateway import Requestable, Gateway
from .interface import LazyLoadable
from .permission import ChannelPermission, PermissionHolder
from .role import Role
from .user import User, GuildUser
from .util import unpack_value, unpack_id


class Channel(LazyLoadable, Requestable, ABC):
    """
    Interface, represents a channel where messages flowing
    """
    type: ChannelTypes

    @abstractmethod
    async def send(self, content: Union[str, List], *, type: MessageTypes = None, **kwargs):
        """
        send a msg to the channel
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def id(self) -> str:
        """the channel's id

        this field should be protected, thus only exported a read-only prop"""
        raise NotImplementedError


class PublicChannel(Channel, PermissionHolder, ABC):
    """the channels in guild, in contrast to PrivateChannel(private chat)"""
    name: str
    user_id: str
    guild_id: str
    topic: str
    is_category: int
    parent_id: str
    level: int

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
        self.permission: ChannelPermission = ChannelPermission(**kwargs)

    async def load(self):
        self._update_fields(**(await self.gate.exec_req(api.Channel.view(self.id))))
        self._loaded = True

    async def update(self, name: str = None, topic: str = None, slow_mode: Union[int, SlowModeTypes] = None) -> dict:
        """
        update channel's settings
        """
        params = {'channel_id': self.id}
        if name is not None:
            params['name'] = name
        if topic is not None:
            params['topic'] = topic
        if slow_mode is not None:
            params['slow_mode'] = unpack_value(slow_mode)
        rt = await self.gate.exec_req(api.Channel.update(**params))
        await self.load()
        return rt

    async def list_users(self,
                         search: str = None,
                         role: Union[Role, str, int] = None,
                         mobile_verified: bool = None,
                         active_time: int = None,
                         joined_at: int = None,
                         page: int = 1,
                         page_size: int = 50,
                         filter_user_id: str = None) -> List[User]:
        """list the users who can see this channel"""
        params = {'guild_id': self.guild_id, 'channel_id': self.id, 'page': page, 'page_size': page_size}
        if search is not None:
            params['search'] = search
        if role is not None:
            params['role_id'] = unpack_id(role)
        if mobile_verified is not None:
            params['mobile'] = 1 if mobile_verified else 0
        if active_time is not None and active_time in [0, 1]:
            params['active_time'] = active_time
        if joined_at is not None and joined_at in [0, 1]:
            params['joined_at'] = joined_at
        if filter_user_id is not None:
            params['filter_user_id'] = filter_user_id
        users = await self.gate.exec_paged_req(api.Guild.userList(**params))
        return [User(_gate_=self.gate, _lazy_loaded_=True, **i) for i in users]

    async def list_messages(self,
                            page_size: int = None,
                            pin: int = None,
                            flag: MessageFlagModes = None,
                            msg_id: str = None) -> Dict:
        """list the messages in this channel (only for public channel now)"""
        params = {'target_id': self.id}
        if page_size is not None:
            params['page_size'] = page_size
        if pin is not None:
            params['pin'] = pin
        if flag is not None:
            params['flag'] = flag
        if msg_id is not None:
            params['msg_id'] = msg_id
        return await self.gate.exec_req(api.Message.list(**params))


class PublicTextChannel(PublicChannel):
    """
    `Standard Object`

    Text chat channels in guild
    """
    slow_mode: int

    def _update_fields(self, **kwargs):
        super()._update_fields(**kwargs)
        self.slow_mode: int = kwargs.get('slow_mode')

    async def send(self, content: Union[str, List], *, type: MessageTypes = None, temp_target_id: str = '', **kwargs):
        """
        send a msg to the channel

        ``temp_target_id`` is available in PublicTextChannel, so ``send()`` is overloaded here
        """
        # if content is card msg, then convert it to plain str
        if isinstance(content, List):
            type = MessageTypes.CARD
            content = json.dumps(content)
        type = type if type is not None else MessageTypes.KMD

        # merge params
        kwargs['target_id'] = self.id
        kwargs['content'] = content
        kwargs['type'] = type.value
        if temp_target_id:
            kwargs['temp_target_id'] = temp_target_id

        return await self.gate.exec_req(api.Message.create(**kwargs))


class PublicVoiceChannel(PublicChannel):
    """
    Voice chat channel in guild

    a placeholder now for future design/adaption
    """

    async def send(self, content: Union[str, List], **kwargs):
        raise TypeError('now there is no PublicVoiceChannel, *hey dude we have a pkg from future*')

    async def move_user(self, *users: Union[User, str]):
        """move users to this public voice channel"""
        user_ids = [u.id if isinstance(u, User) else u for u in users]
        return await self.gate.exec_req(api.Channel.moveUser(target_id=self.id, user_ids=user_ids))

    async def fetch_user_list(self) -> List[GuildUser]:
        """get users chatting in the voice channel"""
        users = await self.gate.exec_req(api.Channel.userList(channel_id=self.id))
        return [GuildUser(_gate_=self.gate, guild_id=self.guild_id, _lazy_loaded_=True, **i) for i in users]


def public_channel_factory(_gate_: Gateway, **kwargs) -> Union[PublicTextChannel, PublicVoiceChannel]:
    """factory function to build a channel object"""
    kwargs['type'] = kwargs['type'] if isinstance(kwargs['type'], ChannelTypes) else ChannelTypes(kwargs['type'])
    if kwargs['type'] == ChannelTypes.TEXT:
        return PublicTextChannel(**kwargs, _gate_=_gate_)
    if kwargs['type'] == ChannelTypes.VOICE:
        return PublicVoiceChannel(**kwargs, _gate_=_gate_)
    raise ValueError(f'unsupported channel type: {kwargs["type"]}: {kwargs}')


class PrivateChannel(Channel):
    """Private chat channel

    a private channel associates the code and another user(called as target in the following)"""

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
        """prop, the target's id"""
        return self.target_info.get('id') if self.target_info else None

    @property
    def target_user_name(self) -> str:
        """prop, the target's name"""
        return self.target_info.get('username') if self.target_info else None

    @property
    def is_target_user_online(self) -> bool:
        """prop, is the target online"""
        return self.target_info.get('online') if self.target_info else None

    @property
    def target_user_avatar(self) -> str:
        """prop, the target's avatar"""
        return self.target_info.get('avatar') if self.target_info else None

    async def send(self, content: Union[str, List], *, type: MessageTypes = None, **kwargs):
        return await User(id=self.id, _gate_=self.gate).send(content, type=type, **kwargs)
