from abc import ABC, abstractmethod
from enum import Enum
from khl.bot import Bot
from khl.message import Msg
from typing import Any, Coroutine, Optional, Sequence


class CommandType(Enum):
    MENU = 'MENU'
    APP = 'APP'


# class BaseSession(ABC):
#     class ResultTypes(Enum):
#         SUCCESS = 'SUCCESS'
#         FAIL = 'FAIL'
#         ERROR = 'ERROR'
#         HELP = 'HELP'

#     command: Any
#     command_str: str
#     args: Sequence[str]
#     msg: Msg
#     bot: Bot
#     result_type: ResultTypes
#     detail: Any

#     @abstractmethod
#     def __init__(self,
#                  command: Any,
#                  command_str: str,
#                  args: Sequence[str],
#                  msg: Msg,
#                  bot: Optional[Bot] = None) -> None:
#         self.command_str = command_str
#         self.command = command
#         self.args = args
#         self.msg = msg
#         self.bot = bot if bot else self.command.bot

#     @abstractmethod
#     async def reply(self,
#                     content: str,
#                     message_type: Msg.Types = Msg.Types.KMD,
#                     result_type: ResultTypes = ResultTypes.SUCCESS):
#         func_result = await self.send(content=content,
#                                       result_type=result_type,
#                                       mention=True,
#                                       reply=True)
#         return func_result

#     @abstractmethod
#     async def reply_only(self,
#                          content: str,
#                          message_type: Msg.Types = Msg.Types.KMD,
#                          result_type: ResultTypes = ResultTypes.SUCCESS):
#         func_result = await self.send(content=content,
#                                       result_type=result_type,
#                                       mention=False,
#                                       reply=True)
#         return func_result

#     @abstractmethod
#     async def mention(self,
#                       content: str,
#                       message_type: Msg.Types = Msg.Types.KMD,
#                       result_type: ResultTypes = ResultTypes.SUCCESS):
#         func_result = await self.send(content=content,
#                                       result_type=result_type,
#                                       mention=True,
#                                       reply=False)
#         return func_result

#     @abstractmethod
#     async def send(self,
#                    content: str,
#                    result_type: ResultTypes = ResultTypes.SUCCESS,
#                    message_channel: Optional[str] = None,
#                    message_type: Msg.Types = Msg.Types.KMD,
#                    mention: bool = False,
#                    reply: bool = False):

#         if (mention):
#             content = f'(met){self.msg.author_id}(met) ' + content
#         quote: str = self.msg.msg_id if (reply) else ''

#         if (not self.bot):
#             raise AttributeError(
#                 'Session send method used before setting a bot.'
#                 f' Command: {self.command.name}')
#         self.msg_sent = await self.bot.send(
#             type=message_type,
#             content=content,
#             channel_id=message_channel
#             if message_channel else self.msg.target_id,
#             quote=quote)
#         print(self.msg_sent)
#         self.result_type = result_type
#         return self
