from typing import Any, Coroutine, Optional, Sequence

from khl.Bot import Bot
from khl.Message import Msg

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
        return await self.send(content, message_type, result_type, True, True)

    async def reply_only(
        self,
        content: str,
        message_type: Msg.Types = Msg.Types.KMD,
        result_type: BaseSession.ResultTypes = BaseSession.ResultTypes.SUCCESS
    ):
        return await self.send(content, message_type, result_type, False, True)

    async def mention(
        self,
        content: str,
        message_type: Msg.Types = Msg.Types.KMD,
        result_type: BaseSession.ResultTypes = BaseSession.ResultTypes.SUCCESS
    ):
        return await self.send(content, message_type, result_type, True, False)

    async def send(self,
                   content: str,
                   message_type: Msg.Types = Msg.Types.KMD,
                   result_type: BaseSession.ResultTypes = BaseSession.
                   ResultTypes.SUCCESS,
                   mention: bool = False,
                   reply: bool = False):
        if (mention):
            content = f'(met){self.msg.author_id}(met) ' + content
        quote: str = self.msg.msg_id if (reply) else ''

        if (not self.bot):
            raise AttributeError('Session send used before assigning a bot.'
                                 f' Command: {self.command.name}')
        self.msg_sent = await self.bot.send(object_name=message_type,
                                            content=content,
                                            channel_id=self.msg.target_id,
                                            quote=quote)
        print(self.msg_sent)
        self.result_type = result_type
        return self
