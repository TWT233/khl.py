from abc import ABC, abstractmethod
from typing import List, Union

from . import api, util
from .role import Role
from .user import User
from .interface import LazyLoadable
from .gateway import Requestable


class RolePermission:
    """part of channel permission, the permission setting for a specific role in the channel

    this setting overwrites the role's permission set in the guild"""
    role_id: int
    allow: int
    deny: int

    def __init__(self, *, role_id: int, allow: int, deny: int, **_):
        self.role_id = role_id
        self.allow = allow
        self.deny = deny


class UserPermission:
    """part of channel permission, the permission setting for a specific user"""
    user: User
    allow: int
    deny: int

    def __init__(self, *, user: User, allow: int, deny: int, **_):
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


class PermissionHolder(LazyLoadable, Requestable, ABC):
    """holder of the permissions, can be a channel or a category"""

    permission: ChannelPermission

    @property
    @abstractmethod
    def id(self) -> str:
        """the channel's id

        this field should be protected, thus only exported a read-only prop"""
        raise NotImplementedError

    async def fetch_permission(self, force_update: bool = True) -> ChannelPermission:
        """fetch permission setting of the channel"""
        if force_update or not self.permission.loaded:
            await self.permission.load()
        return self.permission

    async def create_user_permission(self, target: Union[User, str]):
        """create a customized permission setting entry"""
        t = 'user_id'
        v = util.unpack_id(target)
        d = await self.gate.exec_req(api.ChannelRole.create(channel_id=self.id, type=t, value=v))
        self.permission.loaded = False
        return d

    async def update_user_permission(self, target: Union[User, str], allow: int = 0, deny: int = 0) -> Role:
        """update a customized permission setting entry"""
        t = 'user_id'
        v = util.unpack_id(target)
        return await self.gate.exec_req(
            api.ChannelRole.update(channel_id=self.id, type=t, value=v, allow=allow, deny=deny))

    async def delete_user_permission(self, target: Union[User, str]):
        """delete a customized permission setting entry"""
        t = 'user_id'
        v = util.unpack_id(target)
        return await self.gate.exec_req(api.ChannelRole.delete(channel_id=self.id, type=t, value=v))

    async def create_role_permission(self, target: Union[Role, str]):
        """create a customized permission setting entry"""
        t = 'role_id'
        v = util.unpack_id(target)
        d = await self.gate.exec_req(api.ChannelRole.create(channel_id=self.id, type=t, value=v))
        self.permission.loaded = False
        return d

    async def update_role_permission(self, target: Union[Role, str], allow: int = 0, deny: int = 0) -> Role:
        """update a customized permission setting entry"""
        t = 'role_id'
        v = util.unpack_id(target)
        return await self.gate.exec_req(
            api.ChannelRole.update(channel_id=self.id, type=t, value=v, allow=allow, deny=deny))

    async def delete_role_permission(self, target: Union[Role, str]):
        """delete a customized permission setting entry"""
        t = 'role_id'
        v = util.unpack_id(target)
        return await self.gate.exec_req(api.ChannelRole.delete(channel_id=self.id, type=t, value=v))
