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
                 author: 'User',
                 user_id: Optional[str] = None,
                 msg_ids: Sequence[str] = []):
        self.guild: 'Guild' = guild
        self.channel: 'Channel' = channel
        self.bot: 'Bot' = bot
        self.author: 'User' = author
        self.user_id: str = user_id if user_id else author.id
        self.msg_ids: Sequence[str] = msg_ids

    async def wait_btn(self,
                       ori_msg_id: str,
                       timeout: float = 30) -> 'BtnClickMsg':
        return await self.bot.btn_msg_queue.get(ori_msg_id, timeout)

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
        kwargs['temp_target_id'] = temp_target_id if temp_target_id else self.user_id
        if isinstance(card, dict):
            card = json.dumps(card)
        kwargs['temp_target_id'] = temp_target_id
        return await self.send_card(card, **kwargs)


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

    @staticmethod
    def event_to_msg(event: Dict[Any, Any]):
        if event['type'] == Msg.Types.SYS:
            if event['extra']['type'] == SysMsg.EventTypes.BTN_CLICK.value:
                return BtnClickMsg(**event)
            return SysMsg(**event)
        elif event['type'] == Msg.Types.TEXT:
            return TextMsg(**event)
        elif event['type'] == Msg.Types.KMD:
            return KMDMsg(**event)
        elif event['type'] == Msg.Types.CARD:
            return CardMsg(**event)

    async def reply(self, content: str, **kwargs):
        kwargs['quote'] = self.msg_id
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


class TextMsg(Msg):
    type = Msg.Types.TEXT
    """
    represents a msg, recv from/send to server
    """

    def __init__(self, **kwargs):
        """
        all fields origin from server event object
        corresponding to official doc
        """
        self.channel_type = kwargs['channel_type']
        if self.type != kwargs['type']:
            raise ValueError(f'wrong type found in message: {kwargs}')
        self.target_id = kwargs['target_id']
        self.author_id = kwargs['author_id']
        self.content = kwargs['content']
        self.msg_id = kwargs['msg_id']
        self.msg_timestamp = kwargs['msg_timestamp']
        self.nonce = kwargs['nonce']
        self.extra = kwargs['extra']

        self.author: User = User(self.extra['author'])
        self.ctx = MsgCtx(guild=Guild(self.guild_id),
                          channel=Channel(self.target_id),
                          bot=kwargs['bot'],
                          author=self.author,
                          msg_ids=[self.msg_id])

    @property
    def channel_id(self) -> str:
        return self.target_id

    @property
    def guild_id(self) -> str:
        return self.extra['guild_id']

    @property
    def channel_name(self) -> str:
        return self.extra['channel_name']

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


class SysMsg(Msg):
    sys_event_type: str

    class EventTypes(Enum):
        BTN_CLICK = 'message_btn_click'
        NOTSET = ''

    def __init__(self, **kwargs: Any) -> None:
        self.type = Msg.Types.SYS
        self.event_type = SysMsg.EventTypes.NOTSET
        self.target_id = kwargs['target_id']
        self.author_id = kwargs['author_id']
        self.content = kwargs['content']
        self.msg_id = kwargs['msg_id']
        self.msg_timestamp = kwargs['msg_timestamp']
        self.extra = kwargs['extra']
        self.sys_event_type = kwargs['extra']['type']


class BtnClickMsg(SysMsg):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.event_type = SysMsg.EventTypes.BTN_CLICK

        self.ret_val: str = self.extra['body']['value']
        self.ori_msg_id = self.extra['body']['msg_id']
        self.exe_user_id = self.extra['body']['user_id']
        self.exe_target_id = self.extra['body']['target_id']
        self.ctx = MsgCtx(guild=None,
                          channel=Channel(self.extra['body']['target_id']),
                          bot=kwargs['bot'],
                          author=User({'id': self.extra['body']['user_id']}),
                          msg_ids=[self.extra['body']['msg_id']])

    @property
    def channel_id(self) -> str:
        return self.exe_target_id
