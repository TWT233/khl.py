from abc import ABC
from enum import IntEnum

from typing import List, Any, Mapping, NamedTuple, TYPE_CHECKING

from khl.channel import Channel
from khl.guild import Guild
from khl.user import User

if TYPE_CHECKING:
    from khl.bot import Bot
    from khl.args import BotSendArgs


class MsgCtx:
    """
    represents a context of a msg
    """
    def __init__(self, guild: 'Guild', channel: 'Channel', bot: 'Bot',
                 author: 'User'):
        self.guild: 'Guild' = guild
        self.channel: 'Channel' = channel
        self.bot: 'Bot' = bot
        self.author: 'User' = author

    async def send(self, content: str, **kwargs: 'BotSendArgs') -> Any:
        return await self.bot.send(self.channel.id, content, **kwargs)


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
    """
    represents a msg, recv from/send to server
    """
    def __init__(self, **kwargs):
        """
        all fields origin from server event object
        corresponding to official doc
        """
        self.channel_type = kwargs['channel_type']
        self.type = self.Types.TEXT
        if self.type != kwargs['type']:
            raise ValueError('wrong type')

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
                          author=self.author)

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
                    use_quote: bool = False,
                    use_mention: bool = False):
        await self.ctx.send(
            f"(met){self.author_id}(met)" if use_mention else '' + content,
            quote=self.msg_id if use_quote else '',
            type=Msg.Types.KMD)
