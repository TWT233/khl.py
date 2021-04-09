import json
import logging
from abc import ABC
from enum import Enum, IntEnum
from typing import Dict, List, Any, Mapping, Optional, Sequence, TYPE_CHECKING, Union

from .channel import Channel
from .guild import Guild
from .user import User

if TYPE_CHECKING:
    from .bot import Bot


class MsgCtx:
    logger = logging.getLogger('khl.MsgCtx')
    """
    represents a context of a msg
    """

    def __init__(self,
                 guild: 'Guild',
                 channel: 'Channel',
                 bot: 'Bot',
                 user: 'User',
                 user_id: Optional[str] = None,
                 msg_ids: Sequence[str] = []):
        self.guild: 'Guild' = guild
        self.channel: 'Channel' = channel
        self.bot: 'Bot' = bot
        self.user: 'User' = user
        self.user_id: str = user_id if user_id else user.id
        self.msg_ids: Sequence[str] = msg_ids

    @property
    def author(self) -> 'User':
        return self.user

    @author.setter
    def author(self, value: 'User'):
        self.user = value

    async def wait_btn(self, ori_msg_id: str, timeout: float = 30) -> 'SysMsg':
        return await self.bot.kq['btn'].get(ori_msg_id, timeout)

    async def wait_user(self, user_id: str, timeout: float = 30) -> 'TextMsg':
        return await self.bot.kq['user'].get(user_id, timeout)

    async def send(self, content: str, **kwargs: Any) -> dict:
        return await self.bot.send(self.channel.id, content, **kwargs)

    async def send_card(self, card: Union[list, str], **kwargs):
        if isinstance(card, list):
            card = json.dumps(card)
        kwargs['type'] = Msg.Types.CARD
        return await self.send(card, **kwargs)

    async def send_temp(self,
                        content: str,
                        temp_target_id: Optional[str] = None,
                        **kwargs):
        kwargs[
            'temp_target_id'] = temp_target_id if temp_target_id else self.user_id
        return await self.send(content, **kwargs)

    async def send_card_temp(self,
                             card: Union[list, str],
                             temp_target_id: Optional[str] = None,
                             **kwargs):
        if isinstance(card, list):
            card = json.dumps(card)
        kwargs['type'] = Msg.Types.CARD
        return await self.send_temp(card, temp_target_id, **kwargs)


class Msg(ABC):
    class Types(IntEnum):
        TEXT = 1
        IMG = 2
        VIDEO = 3
        FILE = 4
        AUDIO = 8
        KMD = 9
        CARD = 10
        SYS = 255

    type: Types
    channel_type: str
    target_id: str
    author_id: str
    content: str
    msg_id: str
    msg_timestamp: int
    nonce: str
    extra: Mapping[str, Any]
    ctx: 'MsgCtx'

    def __init__(self, **kwargs):
        """
        all fields origin from server event object
        corresponding to official doc
        """
        self.channel_type = kwargs.get('channel_type')
        self.target_id = kwargs.get('target_id')
        self.author_id = kwargs.get('author_id')
        self.content = kwargs.get('content')
        self.msg_id = kwargs.get('msg_id')
        self.msg_timestamp = kwargs.get('msg_timestamp')
        self.nonce = kwargs.get('nonce')
        self.extra = kwargs.get('extra')

    @staticmethod
    def event_to_msg(event: Dict[Any, Any]):
        if event['type'] == Msg.Types.SYS:
            return SysMsg(**event)
        elif event['type'] == Msg.Types.TEXT:
            return TextMsg(**event)
        elif event['type'] == Msg.Types.IMG:
            return ImgMsg(**event)
        elif event['type'] == Msg.Types.VIDEO:
            return VideoMsg(**event)
        elif event['type'] == Msg.Types.FILE:
            return FileMsg(**event)
        elif event['type'] == Msg.Types.KMD:
            return KMDMsg(**event)
        elif event['type'] == Msg.Types.CARD:
            return CardMsg(**event)
        else:
            return None

    async def reply(self, content: str, **kwargs):
        kwargs['quote'] = self.msg_id

        if self.channel_type == 'PERSON':
            return await self.ctx.bot.send_dm(self.ctx.author.id, content, **kwargs)
        elif self.channel_type == 'GROUP':
            return await self.ctx.bot.send(self.ctx.channel.id, content, **kwargs)
        else:
            raise ValueError(f"Unacceptable channel_type: {self.channel_type}")

    async def reply_temp(self, content: str, **kwargs):
        kwargs['temp_target_id'] = self.author_id
        return await self.reply(content, **kwargs)

    async def reply_card(self, card: Union[list, str], **kwargs):
        if isinstance(card, list):
            card = json.dumps(card)
        kwargs['type'] = Msg.Types.CARD
        return await self.reply(card, **kwargs)

    async def reply_card_temp(self, card: Union[list, str], **kwargs):
        if isinstance(card, list):
            card = json.dumps(card)
        kwargs['type'] = Msg.Types.CARD
        return await self.reply_temp(card, **kwargs)

    async def delete(self):
        return await self.ctx.bot.delete(self.msg_id)


class _NormalMsgKernel(Msg):
    """
    fields shared between all types of msg, except SysMsg
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.author: 'User' = User(self.extra['author'])
        self.ctx = MsgCtx(guild=Guild(self.guild_id),
                          channel=Channel(self.target_id),
                          bot=kwargs.get('bot'),
                          user=self.author,
                          msg_ids=[self.msg_id])

    @property
    def channel_id(self) -> str:
        """
        the channel where this msg sends to
        """
        return self.target_id

    @property
    def channel_name(self) -> str:
        """
        the channel where this msg sends to
        """
        return self.extra.get('channel_name', None)

    @property
    def guild_id(self) -> str:
        """
        the guild of this msg
        """
        return self.extra.get('guild_id', None)


class TextMsg(_NormalMsgKernel):
    """
    represents a msg, recv from/send to server
    """
    type = Msg.Types.TEXT

    @property
    def mention(self) -> List[str]:
        return self.extra['mention']

    @property
    def mention_all(self) -> bool:
        return self.extra['mention_all']

    @property
    def mention_roles(self) -> List[str]:
        return self.extra['mention_roles']

    @property
    def mention_here(self) -> bool:
        return self.extra['mention_heres']


class KMDMsg(TextMsg):
    type = Msg.Types.KMD


class CardMsg(TextMsg):
    type = Msg.Types.CARD


class ImgMsg(_NormalMsgKernel):
    type = Msg.Types.IMG

    @property
    def detail(self) -> dict:
        return self.extra['attachments']

    @property
    def url(self):
        return self.detail['url']

    @property
    def name(self) -> str:
        return self.detail['name']


class VideoMsg(_NormalMsgKernel):
    type = Msg.Types.VIDEO

    @property
    def detail(self) -> dict:
        return self.extra['attachments']

    @property
    def url(self) -> str:
        return self.detail['url']

    @property
    def name(self) -> str:
        return self.detail['name']

    @property
    def file_type(self) -> str:
        return self.detail['file_type']

    @property
    def size(self) -> int:
        return self.detail['size']

    @property
    def duration(self) -> float:
        return self.detail['duration']

    @property
    def width(self) -> int:
        return self.detail['width']

    @property
    def height(self) -> int:
        return self.detail['height']


class FileMsg(_NormalMsgKernel):
    type = Msg.Types.FILE

    @property
    def detail(self) -> dict:
        return self.extra['attachments']

    @property
    def url(self) -> str:
        return self.detail['url']

    @property
    def name(self) -> str:
        return self.detail['name']

    @property
    def file_type(self) -> str:
        return self.detail['file_type']

    @property
    def size(self) -> int:
        return self.detail['size']


class BtnTextMsg(TextMsg):
    def __init__(self, btn: 'SysMsg'):
        """
        all fields origin from server event object
        corresponding to official doc
        """
        trans_msg = {
            "type": 1,
            "channel_type": "GROUP",
            "target_id": btn.extra['body']['target_id'],
            "author_id": btn.author_id,
            "content": btn.extra['body']['value'],
            "msg_id": btn.msg_id,
            "msg_timestamp": btn.msg_timestamp,
            "nonce": "",
            "extra": {
                "type": 1,
                "guild_id": "",
                "channel_name": "",
                "mention": [],
                "mention_all": "False",
                "mention_roles": [],
                "mention_here": "False",
                "nav_channels": [],
                "code": "",
                "author": btn.extra['body']['user_info'],
            },
            "bot": btn.bot
        }
        self.ori_sys_msg = btn
        super().__init__(**trans_msg)

    async def reply(self, content: str, **kwargs):
        return await self.ctx.bot.send(self.ctx.channel.id, content, **kwargs)

    async def reply_temp(self, content: str, **kwargs):
        kwargs['temp_target_id'] = self.author_id
        return await self.reply(content, **kwargs)

    async def reply_card(self, card: Union[list, str], **kwargs):
        if isinstance(card, list):
            card = json.dumps(card)
        kwargs['type'] = Msg.Types.CARD
        return await self.reply(card, **kwargs)

    async def reply_card_temp(self, card: Union[list, str], **kwargs):
        if isinstance(card, list):
            card = json.dumps(card)
        kwargs['type'] = Msg.Types.CARD
        return await self.reply_temp(card, **kwargs)


class SysMsg(Msg):
    type = Msg.Types.SYS

    class EventTypes(Enum):
        UNKNOWN = 0
        BTN_CLICK = 'message_btn_click'

        ADDED_REACTION_GROUP = 'added_reaction'
        DELETED_REACTION_GROUP = 'deleted_reaction'
        UPDATED_MSG_GROUP = 'updated_message'
        DELETED_MSG_GROUP = 'deleted_message'

        PRIVATE_ADDED_REACTION = 'private_added_reaction'
        PRIVATE_DELETED_REACTION = 'private_deleted_reaction'
        UPDATED_PRIVATE_MSG = 'updated_private_message'
        DELETED_PRIVATE_MSG = 'deleted_private_message'

        UPDATED_GUILD = 'updated_guild'

        JOINED_GUILD_MEMBER = 'joined_guild'
        EXITED_GUILD_MEMBER = 'exited_guild'
        GUILD_MEMBER_ONLINE = 'guild_member_online'
        GUILD_MEMBER_OFFLINE = 'guild_member_offline'

        JOINED_CHANNEL_MEMBER = 'joined_channel'
        EXITED_CHANNEL_MEMBER = 'exited_channel'
        UPDATED_GUILD_MEMBER = 'updated_guild_member'

        UPDATED_CHANNEL = 'updated_channel'
        ADDED_CHANNEL = 'added_channel'
        DELETED_CHANNEL = 'deleted_channel'

        NOTSET = ''

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.bot: Bot = kwargs['bot']
        if self.event_type == self.EventTypes.BTN_CLICK:
            self.ctx = MsgCtx(guild=None,
                              channel=Channel(self.extra['body']['target_id']),
                              bot=kwargs['bot'],
                              user=User(self.extra['body']['user_info']),
                              msg_ids=[self.extra['body']['msg_id']])

    @property
    def body(self):
        return self.extra['body']

    @property
    def event_type(self):
        try:
            return SysMsg.EventTypes(self.extra['type'])
        except ValueError:
            self.bot.logger.warning(
                f'unsupported event type "{self.extra["type"]}"')
            return SysMsg.EventTypes.UNKNOWN

    @property
    def sys_event_type(self):
        return self.event_type


class SysMsgAddedReaction(SysMsg):
    @property
    def emoji(self) -> dict:
        return self.body['emoji']

    @property
    def related_msg_id(self) -> str:
        return self.body['msg_id']

    @property
    def operator_id(self) -> str:
        return self.body['user_id']

    @property
    def related_channel_id(self) -> str:
        return self.body['channel_id']


class SysMsgDeletedReaction(SysMsg):
    @property
    def emoji(self) -> dict:
        return self.body['emoji']

    @property
    def related_msg_id(self) -> str:
        return self.body['msg_id']

    @property
    def operator_id(self) -> str:
        return self.body['user_id']

    @property
    def related_channel_id(self) -> str:
        return self.body['channel_id']


class SysMsgUpdatedMessage(SysMsg):
    @property
    def updated_msg_id(self) -> str:
        return self.body['msg_id']

    @property
    def new_content(self) -> str:
        return self.body['content']

    @property
    def related_channel_id(self) -> str:
        return self.body['channel_id']

    @property
    def mention(self) -> list:
        return self.body['mention']

    @property
    def mention_all(self) -> bool:
        return self.body['mention_all']

    @property
    def mention_here(self) -> bool:
        return self.body['mention_here']

    @property
    def mention_roles(self) -> list:
        return self.body['mention_roles']

    @property
    def updated_at(self) -> int:
        return self.body['updated_at']


class SysMsgDeletedMessage(SysMsg):
    @property
    def deleted_msg_id(self) -> str:
        return self.body['msg_id']

    @property
    def related_channel_id(self) -> str:
        return self.body['channel_id']


class SysMsgAddedChannel(SysMsg):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._channel = Channel(**self.body)

    @property
    def added_channel(self) -> Channel:
        return self._channel


class SysMsgUpdatedChannel(SysMsg):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self._channel = Channel(**self.body)

    @property
    def updated_channel(self) -> Channel:
        return self._channel


class SysMsgDeletedChannel(SysMsg):
    @property
    def deleted_channel_id(self):
        return self.body['id']

    @property
    def deleted_at(self) -> int:
        return self.body['deleted_at']


class SysMsgPinnedMessage(SysMsg):
    @property
    def related_channel_id(self) -> str:
        return self.body['channel_id']

    @property
    def operator_id(self) -> str:
        return self.body['operator_id']

    @property
    def pinned_msg_id(self) -> str:
        return self.body['msg_id']


class SysMsgUnpinnedMessage(SysMsg):
    @property
    def related_channel_id(self) -> str:
        return self.body['channel_id']

    @property
    def operator_id(self) -> str:
        return self.body['operator_id']

    @property
    def unpinned_msg_id(self) -> str:
        return self.body['msg_id']


class SysMsgJoinedGuild(SysMsg):
    @property
    def user_id(self) -> str:
        return self.body['user_id']

    @property
    def joined_at(self) -> int:
        return self.body['joined_at']


class SysMsgExitedGuild(SysMsg):
    @property
    def user_id(self) -> str:
        return self.body['user_id']

    @property
    def exited_at(self) -> int:
        return self.body['exited_at']


class SysMsgUpdatedGuildMember(SysMsg):
    @property
    def user_id(self) -> str:
        return self.body['user_id']

    @property
    def new_nickname(self) -> str:
        return self.body['nickname']


class SysMsgGuildMemberOnline(SysMsg):
    @property
    def user_id(self) -> str:
        return self.body['user_id']

    @property
    def online_at(self) -> int:
        return self.body['event_time']

    @property
    def common_guilds(self) -> list:
        return self.body['guilds']


class SysMsgGuildMemberOffline(SysMsg):
    @property
    def user_id(self) -> str:
        return self.body['user_id']

    @property
    def online_at(self) -> int:
        return self.body['event_time']

    @property
    def common_guilds(self) -> list:
        return self.body['guilds']
