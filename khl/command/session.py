from collections.abc import Sequence
from typing import Any, Coroutine, Optional

from khl.Bot import Bot
from khl.command.app import AppCommand
from khl.command.menu import MenuCommand
from khl.command.types import SessionResult, Result
from khl.Message import MsgType, TextMsg


class Session:
    command: AppCommand or MenuCommand
    command_str: str
    args: Sequence[str]
    msg: TextMsg
    bot: Bot

    def __init__(self,
                 command: AppCommand or MenuCommand,
                 args: Sequence[str],
                 msg: TextMsg,
                 bot: Optional[Bot] = None) -> None:
        super().__init__()
        self.command = command
        self.args = args
        self.msg = msg
        self.bot = bot if bot else self.command.bot

    def reply(
        self,
        content: str,
        result_type: Result = Result.SUCCESS
    ) -> Coroutine[Any, Any, SessionResult]:
        func_result = self.send(content=content,
                                result_type=result_type,
                                mention=True,
                                reply=True)
        return func_result

    def reply_only(
        self,
        content: str,
        result_type: Result = Result.SUCCESS
    ) -> Coroutine[Any, Any, SessionResult]:
        func_result = self.send(content=content,
                                result_type=result_type,
                                mention=False,
                                reply=True)
        return func_result

    def mention(
        self,
        content: str,
        result_type: Result = Result.SUCCESS
    ) -> Coroutine[Any, Any, SessionResult]:
        func_result = self.send(content=content,
                                result_type=result_type,
                                mention=True,
                                reply=False)
        return func_result

    async def send(self,
                   content: str,
                   result_type: Result = Result.SUCCESS,
                   message_type: MsgType = MsgType.KMD,
                   mention: bool = False,
                   reply: bool = False) -> SessionResult:

        if (mention):
            content = f'(met){self.msg.author_id}(met) ' + content
        quote: str = self.msg.msg_id if (reply) else ''

        if (not self.bot):
            raise AttributeError('Session send used before assigning a bot.'
                                 f' Command: {self.command.name}')
        msg_sent = self.bot.send(object_name=message_type,
                                 content=content,
                                 channel_id=self.msg.target_id,
                                 quote=quote)
        return SessionResult(result_type=result_type,
                             session=self,
                             msg_sent=msg_sent)
