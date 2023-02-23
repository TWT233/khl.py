"""guild related stuffs: Guild, ChannelCategory"""
import logging
import time
import warnings
from typing import List, Union, Dict, IO

from . import api
from ._types import ChannelTypes, GuildMuteTypes, BadgeTypes
from .channel import Channel, public_channel_factory, PublicChannel, PublicVoiceChannel, PublicTextChannel
from .gateway import Requestable
from .interface import LazyLoadable
from .permission import PermissionHolder, ChannelPermission
from .role import Role
from .user import User, GuildUser
from .util import unpack_id, unpack_value

log = logging.getLogger(__name__)


class GuildBoost:
    """Guild boost"""
    user_id: str
    guild_id: str
    start_time: int
    end_time: int
    user: User

    def __init__(self, **kwargs) -> None:
        self.user_id = kwargs.get('user_id')
        self.guild_id = kwargs.get('guild_id')
        self.start_time = kwargs.get('start_time')
        self.end_time = kwargs.get('end_time')
        self.user = User(**kwargs.get('user'), _gate_=kwargs.get('_gate_', None))


class GuildEmoji(Requestable):
    """
    The custom emojis in the guild
    """
    guild_id: str
    name: str
    id: str
    user: GuildUser

    def __init__(self, **kwargs):
        self.gate = kwargs.get('_gate_', None)
        self.guild_id = kwargs.get("guild_id")
        self.name = kwargs.get("name")
        self.id = kwargs.get("id")
        self.user = GuildUser(_gate_=self.gate, guild_id=self.guild_id, **kwargs.get("user_info"))

    async def update(self, name: str):
        """update this emoji's name"""
        await self.gate.exec_req(api.GuildEmoji.update(id=self.id, name=name))

    async def delete(self):
        """delete this custom emoji"""
        await self.gate.exec_req(api.GuildEmoji.delete(id=self.id))


class ChannelCategory(PermissionHolder, Requestable):
    """represent a channel set"""

    _id: str
    name: str
    master_id: str
    guild_id: str
    level: int
    limit_amount: int
    _channels: List[PublicChannel]

    def __init__(self, **kwargs):
        self.gate = kwargs.get('_gate_', None)
        self.id = kwargs.get('id')
        self._update_fields(**kwargs)

    def _update_fields(self, **kwargs):
        self.name = kwargs.get('name')
        self.master_id = kwargs.get('master_id')
        self.guild_id = kwargs.get('_guild_id_')
        self.level = kwargs.get('level')
        self.limit_amount = kwargs.get('limit_amount')
        self._channels = kwargs.get('channels', [])
        self.permission: ChannelPermission = ChannelPermission(**kwargs)

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value

    async def load(self):
        self._update_fields(**(await self.gate.exec_req(api.Channel.view(self.id))))
        self._loaded = True

    def append(self, *channel: PublicChannel):
        """append var-len channel(s) into this category"""
        self._channels.append(*channel)

    def pop(self, index: int = None) -> PublicChannel:
        """pop a channel(default last) from this category"""
        return self._channels.pop(index)

    async def create_text_channel(self, name: str) -> PublicTextChannel:
        """create a text channel in this channel category

        docs: https://developer.kaiheila.cn/doc/http/channel#%E5%88%9B%E5%BB%BA%E9%A2%91%E9%81%93"""
        params = {'name': name, 'guild_id': self.guild_id, 'parent_id': self.id, 'type': ChannelTypes.TEXT.value}
        pc = public_channel_factory(self.gate, **(await self.gate.exec_req(api.Channel.create(**params))))
        self._channels.append(pc)
        return pc

    async def create_voice_channel(self,
                                   name: str,
                                   limit_amount: int = None,
                                   voice_quality: int = None) -> PublicVoiceChannel:
        """create a channel in this channel category

        docs: https://developer.kaiheila.cn/doc/http/channel#%E5%88%9B%E5%BB%BA%E9%A2%91%E9%81%93"""
        params = {'name': name, 'guild_id': self.guild_id, 'parent_id': self.id, 'type': ChannelTypes.VOICE.value}
        if limit_amount:
            params['limit_amount'] = limit_amount
        if voice_quality:
            params['voice_quality'] = voice_quality
        pc = public_channel_factory(self.gate, **(await self.gate.exec_req(api.Channel.create(**params))))
        self._channels.append(pc)
        return pc

    async def delete_channel(self, channel: Union[Channel, str]):
        """delete a channel from this channel category"""
        channel_id = channel.id if isinstance(channel, Channel) else channel
        if channel_id not in [i.id for i in self._channels]:
            raise ValueError(f'channel {channel_id} is not belongs to this category')
        return await self.gate.exec_req(api.Channel.delete(channel_id))

    def __iter__(self):
        return iter(self._channels)


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
    _channel_categories: Dict[str, ChannelCategory]
    _channels: List[PublicChannel]

    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self._channel_categories = {}
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

    async def fetch_channel_category_list(self, force_update: bool = True) -> List[ChannelCategory]:
        """fetch all channel category as a list"""
        await self.fetch_channel_list(force_update)
        return list(self._channel_categories.values())

    async def fetch_channel_list(self, force_update: bool = True) -> List[PublicChannel]:
        """fetch channel list from khl server"""
        if force_update or self._channels is None:
            raw_list = await self.gate.exec_paged_req(api.Channel.list(guild_id=self.id))
            channels: List[PublicChannel] = []
            channel_categories: Dict[str, ChannelCategory] = {}
            for i in raw_list:
                if i['is_category']:
                    cc = ChannelCategory(_gate_=self.gate, _guild_id_=self.id, **i)
                    channel_categories[cc.id] = cc
                else:
                    channels.append(public_channel_factory(_gate_=self.gate, **i))

            self._channels = []
            for i in channels:
                if i.parent_id in channel_categories:
                    channel_categories[i.parent_id].append(i)
                else:
                    self._channels.append(i)
            self._channel_categories = channel_categories
        return self._merge_channels()

    def _merge_channels(self) -> List[PublicChannel]:
        channels = []
        channels.extend(self._channels)
        for v in self._channel_categories.values():
            channels.extend(v)
        return channels

    @property
    def channels(self) -> List[Channel]:
        """
        get guild's channel list

        RECOMMEND: use ``await fetch_channel_list()``

        CAUTION: please call ``await fetch_me()`` first to load data from khl server

        designed as 'empty-then-fetch' will break the rule 'net-related is async'
        """
        if self.loaded:
            return self._merge_channels()
        raise ValueError('not loaded, please call `await fetch_channel_list()` first')

    async def list_user(self, channel: Union[Channel, str] = None, **kwargs) -> List[User]:
        """list users in the guild/a channel belongs to the guild

        paged req, support standard pagination args

        .. deprecated-removed:: 0.3.2 0.4.0
            use :func:`fetch_user_list()`"""
        warnings.warn("deprecated, alternative: fetch_user_list(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.fetch_user_list(channel, **kwargs)

    async def fetch_user_list(self, channel: Union[Channel, str] = None, **kwargs) -> List[User]:
        """list users in the guild/a channel belongs to the guild

        paged req, support standard pagination args"""
        cid = channel.id if isinstance(channel, Channel) else channel
        params = {'guild_id': self.id}
        if cid is not None:
            params['channel_id'] = cid
        users = await self.gate.exec_paged_req(api.Guild.userList(**params), **kwargs)
        return [User(_gate_=self.gate, _lazy_loaded_=True, **i) for i in users]

    async def fetch_joined_channel(self,
                                   user: Union[User, str],
                                   page: int = 1,
                                   page_size: int = 50) -> List[PublicVoiceChannel]:
        """fetch the channels which the user joined(public voice channel)"""
        channels = await self.gate.exec_paged_req(
            api.ChannelUser.getJoinedChannel(page=page, page_size=page_size, guild_id=self.id, user_id=unpack_id(user)))
        return [PublicVoiceChannel(_gate_=self.gate, _lazy_loaded_=True, **i) for i in channels]

    async def fetch_user(self, user_id: str) -> GuildUser:
        """get user object from user_id, can only fetch user in current guild
        """
        user = await self.gate.exec_req(api.User.view(user_id=user_id, guild_id=self.id))
        return GuildUser(guild_id=self.id, _gate_=self.gate, _lazy_loaded_=True, **user)

    async def set_user_nickname(self, user: Union[User, str], nickname: str):
        """set the user's nickname in this guild"""
        await self.gate.exec_req(api.Guild.nickname(guild_id=self.id, nickname=nickname, user_id=unpack_id(user)))

    async def fetch_roles(self, force_update: bool = True) -> List[Role]:
        """fetch the role list in the guild"""
        if force_update or self._roles is None:
            raw_list = await self.gate.exec_paged_req(api.GuildRole.list(guild_id=self.id))
            self._roles = [Role(**i) for i in raw_list]
        return self._roles

    async def create_role(self, role_name: str) -> Role:
        """create a role in the guild"""
        return Role(**(await self.gate.exec_req(api.GuildRole.create(guild_id=self.id, name=role_name))))

    async def update_role(self, new_role: Role) -> Role:
        """update a role in the guild

        :param new_role an edited role object"""
        return Role(**(await self.gate.exec_req(api.GuildRole.update(guild_id=self.id, **vars(new_role)))))

    async def delete_role(self, role: Union[int, Role]):
        """delete a role from the guild"""
        return await self.gate.exec_req(api.GuildRole.delete(guild_id=self.id, role_id=unpack_id(role)))

    async def grant_role(self, user: Union[User, str], role: Union[Role, int]):
        """
        docs:
        https://developer.kaiheila.cn/doc/http/guild-role#%E8%B5%8B%E4%BA%88%E7%94%A8%E6%88%B7%E8%A7%92%E8%89%B2
        """
        return await self.gate.exec_req(
            api.GuildRole.grant(guild_id=self.id, user_id=unpack_id(user), role_id=unpack_id(role)))

    async def revoke_role(self, user: Union[User, str], role: Union[Role, int]):
        """
        docs:
        https://developer.kaiheila.cn/doc/http/guild-role#%E5%88%A0%E9%99%A4%E7%94%A8%E6%88%B7%E8%A7%92%E8%89%B2
        """
        return await self.gate.exec_req(
            api.GuildRole.revoke(guild_id=self.id, user_id=unpack_id(user), role_id=unpack_id(role)))

    async def create_text_channel(self, name: str, category: Union[str, ChannelCategory] = None) -> PublicTextChannel:
        """create a text channel in the guild

        docs: https://developer.kaiheila.cn/doc/http/channel#%E5%88%9B%E5%BB%BA%E9%A2%91%E9%81%93"""
        params = {'name': name, 'guild_id': self.id, 'type': ChannelTypes.TEXT.value}
        if category:
            params['parent_id'] = unpack_id(category)
        return public_channel_factory(self.gate, **(await self.gate.exec_req(api.Channel.create(**params))))

    async def create_voice_channel(self,
                                   name: str,
                                   category: Union[str, ChannelCategory] = None,
                                   limit_amount: int = None,
                                   voice_quality: int = None) -> PublicVoiceChannel:
        """create a voice channel in the guild

        docs: https://developer.kaiheila.cn/doc/http/channel#%E5%88%9B%E5%BB%BA%E9%A2%91%E9%81%93"""
        params = {'name': name, 'guild_id': self.id, 'type': ChannelTypes.VOICE.value}
        if category:
            params['parent_id'] = unpack_id(category)
        if limit_amount:
            params['limit_amount'] = limit_amount
        if voice_quality:
            params['voice_quality'] = voice_quality
        return public_channel_factory(self.gate, **(await self.gate.exec_req(api.Channel.create(**params))))

    async def create_channel_category(self, name: str) -> ChannelCategory:
        """create a channel category in the guild

        docs: https://developer.kaiheila.cn/doc/http/channel#%E5%88%9B%E5%BB%BA%E9%A2%91%E9%81%93"""
        params = {'guild_id': self.id, 'name': name, 'is_category': 1}
        return ChannelCategory(_gate_=self.gate, **(await self.gate.exec_req(api.Channel.create(**params))))

    async def delete_channel(self, channel: Union[Channel, str]):
        """delete the channel from the guild"""
        return await self.gate.exec_req(api.Channel.delete(unpack_id(channel)))

    async def kickout(self, user: Union[User, str]):
        """kick the user from the guild"""
        return await self.gate.exec_req(api.Guild.kickout(guild_id=self.id, target_id=unpack_id(user)))

    async def leave(self):
        """leave from this guild"""
        return await self.gate.exec_req(api.Guild.leave(guild_id=self.id))

    async def get_mute_list(self, return_type: str = 'detail'):
        """get mute list from this guild

        .. deprecated-removed:: 0.3.2 0.4.0
            use :func:`fetch_mute_list()`"""
        warnings.warn("deprecated, alternative: fetch_mute_list(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return self.fetch_mute_list(return_type)

    async def fetch_mute_list(self, return_type: str = 'detail'):
        """get mute list from this guild"""
        return await self.gate.exec_req(api.GuildMute.list(guild_id=self.id, return_type=return_type))

    async def create_mute(self, user: Union[User, str], type: GuildMuteTypes):
        """create mute on this guild"""
        user_id = user.id if isinstance(user, User) else user
        return await self.gate.exec_req(api.GuildMute.create(guild_id=self.id, user_id=user_id, type=type.value))

    async def delete_mute(self, user: Union[User, str], type: GuildMuteTypes):
        """delete mute from this guild"""
        user_id = user.id if isinstance(user, User) else user
        return await self.gate.exec_req(api.GuildMute.delete(guild_id=self.id, user_id=user_id, type=type.value))

    async def fetch_emoji_list(self) -> List[GuildEmoji]:
        """fetch guild emoji list

        :returns: a list of emoji dict, dict contains {'name', 'id', 'user_info': who uploaded the emoji}
        """
        emojis = await self.gate.exec_paged_req(api.GuildEmoji.list(guild_id=self.id))
        return [GuildEmoji(_gate_=self.gate, guild_id=self.id, **i) for i in emojis]

    async def create_emoji(self, emoji: Union[IO, str], *, name: str = None) -> GuildEmoji:
        """upload a custom emoji to the guild

        :returns: an emoji dict. For emoji dict structure, please refer to fetch_emoji_list() doc
        """
        if isinstance(emoji, str):
            emoji = open(emoji, 'rb')
        params = {'guild_id': self.id, 'emoji': emoji}
        if name is not None:
            params['name'] = name
        emoji_info = await self.gate.exec_req(api.GuildEmoji.create(**params))
        return GuildEmoji(_gate_=self.gate, guild_id=self.id, **emoji_info)

    async def update_emoji(self, emoji: Union[GuildEmoji, str], *, name: str = None):
        """update a custom emoji's name"""
        params = {'id': unpack_id(emoji)}
        if name is not None:
            params['name'] = name
        return await self.gate.exec_req(api.GuildEmoji.update(**params))

    async def delete_emoji(self, emoji: Union[GuildEmoji, str]):
        """delete a custom emoji"""
        return await self.gate.exec_req(api.GuildEmoji.delete(unpack_id(emoji)))

    async def fetch_boost(self, start_time: int = 0, end_time: int = int(time.time()), **kwargs) -> List[GuildBoost]:
        """
        list the boost in guild.

        :param start_time: start_time time stamp (Sec).
        :param end_time: end_time time stamp (Sec). Default to now time.
        """
        boost_list = await self.gate.exec_paged_req(
            api.GuildBoost.history(guild_id=self.id, start_time=start_time, end_time=end_time), **kwargs)
        return [GuildBoost(**item, _gate_=self.gate) for item in boost_list]

    async def fetch_badge(self, style: Union[int, BadgeTypes] = BadgeTypes.NAME) -> bytes:
        """get the badge of the guild"""
        return await self.gate.exec_req(api.Badge.guild(guild_id=self.id, style=unpack_value(style)))
