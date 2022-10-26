from typing import List

from . import api
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
