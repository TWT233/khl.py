import json
from typing import List, Union

from . import api
from ._types import MessageTypes, FriendTypes
from .gateway import Requestable, Gateway
from .interface import LazyLoadable
from .intimacy import Intimacy
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
    gate: Gateway

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', '')
        self._loaded = kwargs.get('_lazy_loaded_', False)
        self.gate = kwargs.get('_gate_', None)
        self._update_fields(**kwargs)

    def _update_fields(self, **kwargs):
        self.username = kwargs.get('username', '')
        self.nickname = kwargs.get('nickname', '')
        self.identify_num = kwargs.get('identify_num', '')
        self.online = kwargs.get('online', False)
        self.bot = kwargs.get('bot', False)
        self.status = kwargs.get('status', 0)
        self.avatar = kwargs.get('avatar', '')
        self.vip_avatar = kwargs.get('vip_avatar', '')
        self.mobile_verified = kwargs.get('mobile_verified', False)

    async def load(self):
        self._update_fields(**(await self.gate.exec_req(api.User.view(self.id))))
        self._loaded = True

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
            type = type or MessageTypes.KMD

        # merge params
        kwargs['target_id'] = self.id
        kwargs['content'] = content
        kwargs['type'] = type.value

        return await self.gate.exec_req(api.DirectMessage.create(**kwargs))

    async def fetch_intimacy(self) -> Intimacy:
        """get the user's intimacy info"""
        return Intimacy(user_id=self.id, **(await self.gate.exec_req(api.Intimacy.index(user_id=self.id))))

    async def update_intimacy(self, score: int = 0, social_info: str = None, img_id: str = None):
        """update the user's intimacy"""
        params = {'user_id': self.id}
        if score is not None:
            params['score'] = score
        if social_info is not None:
            params['social_info'] = social_info
        if img_id is not None:
            params['img_id'] = img_id
        return await self.gate.exec_req(api.Intimacy.update(**params))

    async def add_friend(self):
        """send friend request to the user"""
        await self.gate.exec_req(api.Friend.request(user_code=f'{self.username}#{self.identify_num}', _from=0))

    async def block(self):
        """block the user"""
        await self.gate.exec_req(api.Friend.block(user_id=self.id))


class GuildUser(User):
    """a user in guild

    with some fields more than User"""
    guild_id: str
    joined_at: int
    active_time: int
    roles: List[int]
    gate: Gateway

    def _update_fields(self, **kwargs):
        super()._update_fields(**kwargs)
        self.roles = kwargs.get('roles', [])
        self.guild_id = kwargs.get('guild_id', '')
        self.joined_at = kwargs.get('joined_at', 0)
        self.active_time = kwargs.get('active_time', 0)

    async def load(self):
        self._update_fields(**(await self.gate.exec_req(api.User.view(self.id, self.guild_id))))
        self._loaded = True

    async def fetch_roles(self, **kwargs) -> List[Role]:
        """
        Get the user roles in this guild

        paged req, support standard pagination args

        :return: A list for Role
        """
        guild_roles = (await self.gate.exec_paged_req(api.GuildRole.list(self.guild_id), **kwargs))
        rt: List[Role] = []
        for role in guild_roles:
            if role['role_id'] in self.roles:
                rt.append(Role(**role))
        return rt

    async def set_nickname(self, nickname: str):
        """
        Set user's nickname
        """
        await self.gate.exec_req(api.Guild.nickname(guild_id=self.guild_id, nickname=nickname, user_id=self.id))

    async def add_friend(self):
        await self.gate.exec_req(
            api.Friend.request(user_code=f'{self.username}#{self.identify_num}', _from=2, guild_id=self.guild_id))


class Friend:
    """
    Friend with specific friend id and friend info
    """

    gate: Gateway

    id: int
    user_id: str

    _user: User
    _type: FriendTypes

    def __init__(self, _gate_: Gateway, **kwargs):
        self.gate = _gate_
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self._type = kwargs.get('type')

    async def fetch_user(self) -> User:
        """get user"""
        if self._user is None:
            self._user = User(_gate_=self.gate, **(await self.gate.exec_req(api.User.view(user_id=self.user_id))))
        return self._user

    async def delete(self):
        """delete the friend"""
        await self.gate.exec_req(api.Friend.delete(user_id=self.user_id))

    async def block(self):
        """block the user"""
        await self.gate.exec_req(api.Friend.block(user_id=self.user_id))

    async def unblock(self):
        """unblock the blocked user"""
        await self.gate.exec_req(api.Friend.unblock(user_id=self.user_id))

    @property
    def type(self) -> FriendTypes:
        """the type of the friend"""
        return self._type


class FriendRequest(Friend):
    """
    Friend request with specific id and user info
    """

    async def accept(self):
        """accept the friend request"""
        await self.gate.exec_req(api.Friend.handleRequest(id=self.id, accept=1))
        return Friend(_gate_=self.gate, user_id=self.user_id)

    async def deny(self):
        """deny the friend request"""
        await self.gate.exec_req(api.Friend.handleRequest(id=self.id, accept=0))

    @property
    def type(self) -> FriendTypes:
        return FriendTypes.REQUEST
