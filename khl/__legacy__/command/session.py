from abc import ABC
from enum import Enum
from typing import Any, Optional, Sequence, TYPE_CHECKING

from khl.message import Msg

if TYPE_CHECKING:
    from khl.command import Command


class BaseSession(ABC):
    class ResultTypes(Enum):
        SUCCESS = 'SUCCESS'
        FAIL = 'FAIL'
        ERROR = 'ERROR'
        HELP = 'HELP'

    command: 'Command'
    command_str: str
    args: Sequence[str]
    msg: Msg
    bot: Any
    result_type: ResultTypes
    detail: Any


class Session(object):
    class ResultTypes(Enum):
        SUCCESS = 'SUCCESS'
        FAIL = 'FAIL'
        ERROR = 'ERROR'
        HELP = 'HELP'

    command: 'Command'
    command_str: str
    args: Sequence[str]
    msg: Msg
    bot: Any

    def __init__(self,
                 command: 'Command',
                 command_str: str,
                 args: Sequence[str],
                 msg: Msg,
                 bot: Any = None) -> None:
        """[summary]

        Args:
            command (Command): [description]
            command_str (str): [description]
            args (Sequence[str]): [description]
            msg (Msg): [description]
            bot (Optional[Bot], optional): [description]. Defaults to None.
        """
        self.command_str = command_str
        self.command = command
        self.args = args
        self.msg = msg
        self.bot = bot if bot else self.command.bot

    async def reply(
        self,
        content: str,
        message_type: Msg.Types = Msg.Types.KMD,
        result_type: BaseSession.ResultTypes = BaseSession.ResultTypes.SUCCESS
    ):
        """Reply message from sender with quote and mention in same channel.

        Args:
            content (str): Content of the sending message
            result_type (Session.ResultTypes, optional): Result of execution
                Defaults to Session.ResultTypes.SUCCESS.
            message_type (Msg.Types, optional): Type of the sending message.
                Defaults to Msg.Types.KMD.

        Returns:
            self: returns session itself after sending msg.
        """
        return await self.send(content, result_type, None, message_type, True,
                               True)

    async def reply_only(
        self,
        content: str,
        message_type: Msg.Types = Msg.Types.KMD,
        result_type: BaseSession.ResultTypes = BaseSession.ResultTypes.SUCCESS
    ):
        """Reply message from sender with QUOTE ONLY in same channel.

        Args:
            content (str): Content of the sending message
            result_type (Session.ResultTypes, optional): Result of execution
                Defaults to Session.ResultTypes.SUCCESS.
            message_type (Msg.Types, optional): Type of the sending message.
                Defaults to Msg.Types.KMD.

        Returns:
            self: returns session itself after sending msg.
        """
        return await self.send(content, result_type, None, message_type, False,
                               True)

    async def mention(
        self,
        content: str,
        message_type: Msg.Types = Msg.Types.KMD,
        result_type: BaseSession.ResultTypes = BaseSession.ResultTypes.SUCCESS
    ):
        """Reply message from sender with MENTION ONLY in same channel.

        Args:
            content (str): Content of the sending message
            result_type (Session.ResultTypes, optional): Result of execution
                Defaults to Session.ResultTypes.SUCCESS.
            message_type (Msg.Types, optional): Type of the sending message.
                Defaults to Msg.Types.KMD.

        Returns:
            self: returns session itself after sending msg.
        """
        return await self.send(content, result_type, None, message_type, True,
                               False)

    async def send(self,
                   content: str,
                   result_type: BaseSession.ResultTypes = BaseSession.
                   ResultTypes.SUCCESS,
                   message_channel: Optional[str] = None,
                   message_type: Msg.Types = Msg.Types.KMD,
                   mention: bool = False,
                   reply: bool = False):
        """Send message to a channel, normally for replying.

        Args:
            content (str): Content of the sending message
            result_type (Session.ResultTypes, optional): Result of execution.
                Defaults to Session.ResultTypes.SUCCESS.
            message_channel (Optional[str], optional): Channel of the sending message.
                Defaults to None, send in the same channel as user.
            message_type (Msg.Types, optional): Defaults to Msg.Types.KMD, kmarkdown.
            mention (bool, optional): Mention user. Defaults to False.
            reply (bool, optional): Quote user. Defaults to False.

        Raises:
            AttributeError: [description]

        Returns:
            [type]: [description]
        """
        if mention:
            content = f'(met){self.msg.author_id}(met) ' + content
        quote: str = self.msg.msg_id if reply else ''

        if not self.bot:
            raise AttributeError(
                'Session send method used before setting a bot.'
                f' Command: {self.command.name}')
        self.msg_sent = await self.bot.post(
            type=message_type,
            content=content,
            channel_id=message_channel
            if message_channel else self.msg.target_id,
            quote=quote)
        self.result_type = result_type
        return self
