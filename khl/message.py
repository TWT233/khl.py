from abc import ABC
from enum import IntEnum
from typing import List

from .bot import Bot
from .channel import Channel
from .guild import Guild
from .user import User


class MsgCtx:
    """
    represents a context of a msg
    """
    def __init__(self, guild: Guild, channel: Channel, receiver: Bot,
                 sender: User):
        self.guild: Guild = guild
        self.channel: Channel = channel
        self.receiver: Bot = receiver
        self.sender: User = sender

    async def send(self, content: str):
        await self.receiver.send(self.channel.id, content)


class Msg(ABC):
    class Types(IntEnum):
        TEXT = 1
        IMG = 2
        VIDEO = 3
        FILE = 4
        AUDIO = 8
        KMD = 9
        CARD = 10

    type: Types
    channel_type: str
    target_id: str
    author_id: str
    content: str
    msg_id: str
    msg_timestamp: int
    nonce: str
    extra: dict


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

        self.author: User = User(self.extra['author'])

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
