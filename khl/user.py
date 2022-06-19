import json
from typing import List, Union

from . import api
from .gateway import Requestable
from .interface import LazyLoadable, MessageTypes
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

    _loaded: bool

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

        self._loaded = kwargs.get('_lazy_loaded_', False)
        self.gate = kwargs.get('_gate_', None)

    async def load(self):
        pass

    async def send(self, content: Union[str, List], *, type: MessageTypes = None, **kwargs):
        """
        send a msg to a channel

        ``temp_target_id`` is only available in ChannelPrivacyTypes.GROUP
        """
        # if content is card msg, then convert it to plain str
        if isinstance(content, List):
            type = MessageTypes.CARD
            content = json.dumps(content)
        else:
            type = type if type is not None else MessageTypes.KMD

        # merge params
        kwargs['target_id'] = self.id
        kwargs['content'] = content
        kwargs['type'] = type.value

        return await self.gate.exec_req(api.DirectMessage.create(**kwargs))
