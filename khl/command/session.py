from collections.abc import Sequence
from typing import Any, Optional
from khl.command.types import Result
from khl.command.menu import MenuCommand
from khl.command.app import AppCommand

from khl.Bot import Bot

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

    async def send(self,
                   content: str,
                   result_type: Result = Result.SUCCESS,
                   mention: bool = False,
                   reply: bool = False) -> Any:

        if (mention):
            content = f'(met){self.msg.author_id}(met) ' + content
        quote: str = self.msg.msg_id if (reply) else ''

        if (not self.bot):
            raise AttributeError('Session send used before assigning a bot.'
                                 f' Command: {self.command.name}')
        msg_sent = self.bot.send(object_name=MsgType.KMD,
                                 content=content,
                                 channel_id=self.msg.target_id,
                                 quote=quote)
        return msg_sent
