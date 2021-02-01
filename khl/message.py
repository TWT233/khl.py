from abc import ABC
from enum import Enum, IntEnum
import re

from typing import Coroutine, List, Any, Mapping, NamedTuple, Optional, Sequence, TYPE_CHECKING

from aiohttp import ClientResponse

from khl.channel import Channel
from khl.guild import Guild
from khl.user import User
import logging

if TYPE_CHECKING:
    from khl.bot import Bot
    from khl.command import Command


class MsgCtx:
    command: Optional['Command'] = None
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

    # async def set_reply_trigger(self, condition: re.Pattern[Any],
    #                             callback):
    #     async def trigger(msg: Any):
    #         if condition.search(msg.content):
    #             callback(msg.content)
    #     self.bot.on_message(trigger)

    async def send_card(self, content: str):
        return await self.send(content, False, False, 10)

    async def send_card_temp(self, content: str):
        return await self.send(content, True, False, 10, None, self.user_id)

    async def mention(self, content: str):
        return await self.send(content, True, False)

    async def reply_card_temp(self, content: str):
        return await self.send(content, False, True, 10, None, self.user_id)

    async def reply_card(self, content: str):
        return await self.send(content, False, True, 10)

    async def reply(self, content: str):
        """
        reply with mention
        """
        return await self.send(content, True, True)

    async def reply_only(self, content: str):
        """
        reply without mention
        """
        return await self.send(content, False, True)

    async def send(self,
                   content: str,
                   mention: bool = False,
                   reply: bool = False,
                   type: int = 9,
                   channel_id: Optional[str] = None,
                   temp_target_id: Optional[str] = None,
                   **kwargs: Any) -> ClientResponse:
        if mention:
            content = f'(met){self.user_id}(met) ' + content
        if reply:
            if kwargs.get('quote'):
                logging.debug(
                    'reply is true but already defined in kwargs. use kwargs.')
            else:
                kwargs['quote'] = self.msg_ids[-1]
        if type:
            if kwargs.get('type'):
                logging.debug(
                    'type is used but already defined in kwargs. use kwargs.')
            else:
                kwargs['type'] = type

        channel_id = channel_id if channel_id else self.channel.id

        if mention and type == 10:
            logging.warning(
                f'used card message with mention in {self.command.name}')
            mention = False

        if temp_target_id:
            kwargs['temp_target_id'] = temp_target_id

        return await self.bot.send(channel_id, content, **kwargs)


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

        self.author: User = User(self.extra['author'], kwargs['bot'])
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

    async def reply(self,
                    content: str,
                    use_quote: bool = True,
                    use_mention: bool = False):
        return await self.ctx.send(
            (f"(met){self.author_id}(met)" if use_mention else '') + content,
            quote=self.msg_id if use_quote else '',
            type=Msg.Types.KMD)


class KMarkdownMsg(TextMsg):
    type = Msg.Types.KMD


class _SystemMsg(Msg):
    __slots__ = ['event']

    class EventTypes(Enum):
        button = 'message_btn_click'

    def __init__(self, **kwargs: Any) -> None:
        self.type = Msg.Types.SYS
        self.target_id = kwargs['target_id']
        self.author_id = kwargs['author_id']
        self.content = kwargs['content']
        self.msg_id = kwargs['msg_id']
        self.msg_timestamp = kwargs['msg_timestamp']
        self.extra = kwargs['extra']


class SystemMsg(_SystemMsg):
    event: _SystemMsg.EventTypes

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.event = kwargs['extra']['type']
        if self.event == self.EventTypes.button:
            self.button_value = self.extra['body']['value']
            self.ctx = MsgCtx(
                guild=None,
                channel=Channel(self.extra['body']['target_id']),
                bot=kwargs['bot'],
                author=User({'id': self.extra['body']['user_id']},
                            kwargs['bot']),
                msg_ids=[self.extra['body']['msg_id']])
