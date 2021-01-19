from typing import Any, Coroutine, Optional, Sequence

from khl.bot import Bot
from khl.message import Msg

from .typings import BaseSession
from .typings.base_command import BaseCommand


class Session(BaseSession):
    command: BaseCommand
    command_str: str
    args: Sequence[str]
    msg: Msg
    bot: Bot

    def __init__(self,
                 command: BaseCommand,
                 command_str: str,
                 args: Sequence[str],
                 msg: Msg,
                 bot: Optional[Bot] = None) -> None:
        """[summary]

        Args:
            command (BaseCommand): [description]
            command_str (str): [description]
            args (Sequence[str]): [description]
            msg (Msg): [description]
            bot (Optional[Bot], optional): [description]. Defaults to None.
        """
        super().__init__(command=command,
                         command_str=command_str,
                         args=args,
                         msg=msg,
                         bot=bot)

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
        if (mention):
            content = f'(met){self.msg.author_id}(met) ' + content
        quote: str = self.msg.msg_id if (reply) else ''

        if (not self.bot):
            raise AttributeError(
                'Session send method used before setting a bot.'
                f' Command: {self.command.name}')
        self.msg_sent = await self.bot.send(
            object_name=message_type,
            content=content,
            channel_id=message_channel
            if message_channel else self.msg.target_id,
            quote=quote)
        print(self.msg_sent)
        self.result_type = result_type
        return self
