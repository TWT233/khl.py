from typing import List, Union

from . import api
from .channel import PrivateChannel
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

    _loaded: bool
    _channel: PrivateChannel

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
        self._channel = kwargs.get('_channel_')
        self.gate = kwargs.get('_gate_', None)

    async def load(self):
        pass

    async def send(self, content: Union[str, List], **kwargs):
        """
        send a msg to a channel

        ``temp_target_id`` is only available in ChannelPrivacyTypes.GROUP
        """
        if not self._channel:
            self._channel = PrivateChannel(**(await self.gate.exec_req(api.UserChat.create(target_id=self.id))),
                                           _lazy_loaded_=True, _gate_=self.gate)

        return await self._channel.send(content, **kwargs)
