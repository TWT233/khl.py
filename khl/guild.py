from typing import List, Dict

import api
from .channel import Channel, PublicTextChannel, PublicVoiceChannel
from .gateway import Requestable
from .interface import LazyLoadable, ChannelTypes
from .role import Role


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
    roles: List[Role]
    _channel_categories: List[Dict]
    _channels: List[Channel]

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
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
        self.roles = kwargs.get('roles', [])
        self._channel_categories = []
        self._channels = kwargs.get('channels', None)

        self._loaded = kwargs.get('_lazy_loaded_', False)
        self.gate = kwargs.get('_gate_', None)

    async def load(self):
        pass

    async def fetch_channel_list(self, force_update: bool = True) -> List[Channel]:
        if force_update or self._channels is None:
            raw_list = await self.gate.exec_pagination_req(api.Channel.list(guild_id=self.id))
            channel_list: List[Channel] = []
            for i in raw_list:
                if i['type'] == ChannelTypes.CATEGORY:
                    self._channel_categories.append(i)
                elif i['type'] == ChannelTypes.TEXT:
                    channel_list.append(PublicTextChannel(**i))
                elif i['type'] == ChannelTypes.VOICE:
                    channel_list.append(PublicVoiceChannel(**i))
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
