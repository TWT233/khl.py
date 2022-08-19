"""abstraction of khl concept channel: where messages flow in"""
import json
from abc import ABC, abstractmethod
from typing import Union, List, Dict, Optional

from . import api
from .gateway import Requestable, Gateway
from .interface import LazyLoadable
from .role import Role
from ._types import MessageTypes, ChannelTypes, SlowModeTypes
from .user import User
from .util import unpack_value


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


class RolePermission:
    """part of channel permission, the permission setting for a specific role in the channel

    this setting overwrites the role's permission set in the guild"""
    role_id: int
    allow: int
    deny: int

    def __init__(self, *, role_id: int, allow: int, deny: int):
        self.role_id = role_id
        self.allow = allow
        self.deny = deny


class UserPermission:
    """part of channel permission, the permission setting for a specific user"""
    user: User
    allow: int
    deny: int

    def __init__(self, *, user: User, allow: int, deny: int):
        self.user = user
        self.allow = allow
        self.deny = deny


class ChannelPermission(LazyLoadable, Requestable):
    """permission settings in a channel, which can be customized.

    the custom permission entry can be divided into two types:
    1. customized role permission: overwrites the role's global permission settings
    2. customized user permission: exclusively set a user's permission in the channel
    """
    _id: str  # bound channel id
    _sync: int

    roles: List[RolePermission]
    users: List[UserPermission]

    @property
    def id(self) -> str:
        """which channel the permission belongs to"""
        return self._id

    @property
    def sync(self) -> bool:
        """if this channel's permission sync with category"""
        return self._sync != 0

    @sync.setter
    def sync(self, value: bool):
        self._sync = 1 if value else 0

    def __init__(self, **kwargs):
        self._id: str = kwargs.get('id')
        self.gate = kwargs.get('_gate_')
        self._load_fields(**kwargs)

    def _load_fields(self, **kwargs):
        self.roles = [RolePermission(**i) for i in kwargs.get('permission_overwrites', [])]
        self.users = [UserPermission(**i) for i in kwargs.get('permission_users', [])]
        self._sync = kwargs.get('permission_sync', None)
        if self.roles and self.users and (self._sync is not None):
            self._loaded = True

    async def load(self):
        self._load_fields(**await self.gate.exec_req(api.ChannelRole.index(channel_id=self.id)))


class PublicChannel(Channel, ABC):
    """the channels in guild, in contrast to PrivateChannel(private chat)"""
    name: str
    user_id: str
    guild_id: str
    topic: str
    is_category: int
    parent_id: str
    level: int
    permission: ChannelPermission

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

    async def fetch_permission(self, force_update: bool = True) -> ChannelPermission:
        """fetch permission setting of the channel"""
        if force_update or not self.permission.loaded:
            await self.permission.load()
        return self.permission

    async def create_user_permission(self, target: Union[User, str]):
        """create a customized permission setting entry

        for permission setting entry, please refer to `ChannelPermission`"""
        t = 'user_id'
        v = target.id if isinstance(target, User) else target
        d = await self.gate.exec_req(api.ChannelRole.create(channel_id=self.id, type=t, value=v))
        self.permission.loaded = False
        return d

    async def update_user_permission(self, target: Union[User, str], allow: int = 0, deny: int = 0) -> Role:
        """update a customized permission setting entry

        for permission setting entry, please refer to `ChannelPermission`"""
        t = 'user_id'
        v = target.id if isinstance(target, User) else target
        return await self.gate.exec_req(
            api.ChannelRole.update(channel_id=self.id, type=t, value=v, allow=allow, deny=deny))

    async def delete_user_permission(self, target: Union[User, str]):
        """delete a customized permission setting entry

        for permission setting entry, please refer to `ChannelPermission`"""
        t = 'user_id'
        v = target.id if isinstance(target, User) else target
        return await self.gate.exec_req(api.ChannelRole.delete(channel_id=self.id, type=t, value=v))

    async def create_role_permission(self, target: Union[Role, str]):
        """create a customized permission setting entry

        for permission setting entry, please refer to `ChannelPermission`"""
        t = 'role_id'
        v = target.id if isinstance(target, Role) else target
        d = await self.gate.exec_req(api.ChannelRole.create(channel_id=self.id, type=t, value=v))
        self.permission.loaded = False
        return d

    async def update_role_permission(self, target: Union[Role, str], allow: int = 0, deny: int = 0) -> Role:
        """update a customized permission setting entry

        for permission setting entry, please refer to `ChannelPermission`"""
        t = 'role_id'
        v = target.id if isinstance(target, Role) else target
        return await self.gate.exec_req(
            api.ChannelRole.update(channel_id=self.id, type=t, value=v, allow=allow, deny=deny))

    async def delete_role_permission(self, target: Union[Role, str]):
        """delete a customized permission setting entry

        for permission setting entry, please refer to `ChannelPermission`"""
        t = 'role_id'
        v = target.id if isinstance(target, Role) else target
        return await self.gate.exec_req(api.ChannelRole.delete(channel_id=self.id, type=t, value=v))


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


def public_channel_factory(_gate_: Gateway, **kwargs) -> Optional[PublicChannel]:
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
