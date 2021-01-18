from abc import ABC
from enum import IntEnum
from typing import Any, Mapping
from .User import User


class MsgType(IntEnum):
    TEXT = 1
    KMD = 9
    CARD = 10

class BaseMsg(ABC):
    type: MsgType
    target_id:str


class TextMsg(BaseMsg):
    """
    represents a msg, recv from/send to server
    """*
    def __init__(self, *, channel_type: str, target_id: str, author_id: str,
                 content: str, msg_id: str, msg_timestamp: int, nonce: str,
                 extra:Mapping[str, Any]):
        """
        all fields origin from server event object, corresponding to official doc
        """
        self.channel_type = channel_type
        self.type = MsgType.TEXT
        self.target_id = target_id
        self.author_id = author_id
        self.content = content
        self.msg_id = msg_id
        self.msg_timestamp = msg_timestamp
        self.nonce = nonce

        self.guild_id: str = extra['guild_id']
        self.channel_name: str = 'channel_name' in extra.keys(
        ) and extra['channel_name'] or ''
        self.mention: list[str] = extra['mention']
        self.mention_all: bool = extra['mention_all']
        self.mention_roles: list[str] = extra['mention_roles']
        self.mention_here: bool = extra['mention_here']
        self.author: User = User(extra['author'])

