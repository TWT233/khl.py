from .session import Session
from .types import Result, SessionResult
from .menu import MenuCommand
from .base import BaseCommand
from khl.Message import BaseMsg
from typing import Sequence, Union, overload


class AppCommand(BaseCommand):
    intro: str
    parent: MenuCommand or None

    def __init__(self) -> None:
        super().__init__()

    async def execute(self, command_str: str, arg_list: Sequence[str],
                      msg: BaseMsg) -> Result or None:
        return await self.run_func(Session(
            self,
            command_str,
            arg_list,
            msg,
        ))

    # async def execute(self, session: Session) -> Result or None:
    #     return await self.run_func(session)

    async def run_func(self, session: Session) -> Result or None:
        if (not self.bot):
            raise AttributeError(
                f'Trigger {self.trigger}({self.__class__.__name__}) '
                'used before bot is assigned')
        if (self.use_help and session.args[0] == '帮助'):
            await session.reply(self.help)
            return Result.HELP
        result: Union[Result, None, SessionResult] = await self.__func(session)
        if (not result):
            return Result.SUCCESS
        elif isinstance(result, SessionResult):
            return result.result_type
        else:
            return result

    async def __func(self,
                     session: Session) -> Union[Result, None, SessionResult]:
        return super().__func(session)
