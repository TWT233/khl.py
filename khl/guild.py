from typing import List, Dict, Union

from . import api
from .channel import Channel, public_channel_factory
from .gateway import Requestable
from .interface import LazyLoadable, ChannelTypes
from .role import Role
from .user import User


class Guild(LazyLoadable, Requestable):
    """
    `Standard Object`

    represent a server where users gathered in and contains channels
    """
    id: str
    name: str
    topic: str
    master_id: str
    icon: str
    notify_type: int
    region: str
    enable_open: bool
    open_id: str
    default_channel_id: str
    welcome_channel_id: str
    _roles: List[Role]
    _channel_categories: List[Dict]
    _channels: List[Channel]

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self._channel_categories = []
        self._loaded = kwargs.get('_lazy_loaded_', False)
        self.gate = kwargs.get('_gate_', None)
        self._update_fields(**kwargs)

    def _update_fields(self, **kwargs):
        self.name = kwargs.get('name', '')
        self.topic = kwargs.get('topic', '')
        self.master_id = kwargs.get('master_id', '')
        self.icon = kwargs.get('icon', '')
        self.notify_type = kwargs.get('notify_type', 0)
        self.region = kwargs.get('region', '')
        self.enable_open = kwargs.get('enable_open', False)
        self.open_id = kwargs.get('open_id', '')
        self.default_channel_id = kwargs.get('default_channel_id', '')
        self.welcome_channel_id = kwargs.get('welcome_channel_id', '')
        self._roles = kwargs.get('roles', None)
        self._channels = kwargs.get('channels', None)

    async def load(self):
        self._update_fields(**(await self.gate.exec_req(api.Guild.view(self.id))))
        self._loaded = True

    async def fetch_channel_list(self, force_update: bool = True) -> List[Channel]:
        if force_update or self._channels is None:
            raw_list = await self.gate.exec_pagination_req(api.Channel.list(guild_id=self.id))
            channel_list: List[Channel] = []
            for i in raw_list:
                if i['type'] == ChannelTypes.CATEGORY:
                    self._channel_categories.append(i)
                else:
                    channel_list.append(public_channel_factory(_gate_=self.gate, **i))
            self._channels = channel_list
        return self._channels

    @property
    def channels(self) -> List[Channel]:
        """
        get guild's channel list

        RECOMMEND: use ``await fetch_channel_list()``

        CAUTION: please call ``await fetch_me()`` first to load data from khl server

        designed as 'empty-then-fetch' will break the rule 'net-related is async'
        """
        if self._channels is not None:
            return self._channels
        raise ValueError('not loaded, please call `await fetch_channel_list()` first')

    async def fetch_roles(self, force_update: bool = True) -> List[Role]:
        if force_update or self._roles is None:
            raw_list = await self.gate.exec_pagination_req(api.GuildRole.list(guild_id=self.id))
            self._roles = [Role(**i) for i in raw_list]
        return self._roles

    async def create_role(self, role_name: str) -> Role:
        return Role(**(await self.gate.exec_req(api.GuildRole.create(guild_id=self.id, name=role_name))))

    async def update_role(self, new_role: Role) -> Role:
        return Role(**(await self.gate.exec_req(api.GuildRole.update(guild_id=self.id, **vars(new_role)))))

    async def delete_role(self, role_id: int):
        return await self.gate.exec_req(api.GuildRole.delete(guild_id=self.id, role_id=role_id))

    async def kickout(self, user: Union[User, str]):
        target_id = user.id if isinstance(user, User) else user
        return await self.gate.exec_req(api.Guild.kickout(guild_id=self.id, target_id=target_id))
