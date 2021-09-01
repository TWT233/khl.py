from typing import List

from .gateway import LazyLoadable
from .channel import Channel
from .role import Role


class Guild(LazyLoadable):
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
    channels: List[Channel]

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', '')
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
        self.roles = kwargs.get('roles', '')
        self.channels = kwargs.get('channels', '')

        self._loaded = kwargs.get('_lazy_loaded_', False)
        self._gate = kwargs.get('_gate_', None)

    async def load(self):
        pass
