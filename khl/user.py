from typing import List

from .gateway import Requestable
from .interface import LazyLoadable
from .role import Role


class User(LazyLoadable, Requestable):
    """
    `Standard Object`

    represent a entity that interact with khl server
    """
    id: str
    username: str
    nickname: str
    identify_num: str
    online: bool
    bot: bool
    status: int
    avatar: str
    vip_avatar: str
    mobile_verified: bool
    roles: List[Role]

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', '')
        self.username = kwargs.get('username', '')
        self.nickname = kwargs.get('nickname', '')
        self.identify_num = kwargs.get('identify_num', '')
        self.online = kwargs.get('online', False)
        self.bot = kwargs.get('bot', False)
        self.status = kwargs.get('status', 0)
        self.avatar = kwargs.get('avatar', '')
        self.vip_avatar = kwargs.get('vip_avatar', '')
        self.mobile_verified = kwargs.get('mobile_verified', False)
        self.roles = kwargs.get('roles', [])

        self._loaded = kwargs.get('_lazy_loaded_', False)
        self.gate = kwargs.get('_gate_', None)

    async def load(self):
        pass
