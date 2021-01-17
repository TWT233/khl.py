from khl.Message import TextMsg
from typing import Sequence, Union, overload
from khl.command.types import SessionResult, Result
from khl.command.session import Session
from khl.command.base import BaseCommand
from khl.command.menu import MenuCommand


class AppCommand(BaseCommand):
    intro: str
    parent: MenuCommand or None

    def __init__(self) -> None:
        super().__init__()

    @overload
    async def exec(self, command_str: str, args: Sequence[str], msg: TextMsg) -> Result or None:
        return await self.run_func(Session(self, command_str, args, msg, ))

    async def exec(self, session: Session) -> Result or None:
        return await self.run_func(session)

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
