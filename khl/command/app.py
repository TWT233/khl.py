from typing import Union
from khl.command.types import SessionResult, Result
from khl.command.session import Session
from khl.command.base import BaseCommand
from khl.command.menu import MenuCommand


class AppCommand(BaseCommand):
    intro: str
    parent: MenuCommand or None

    def __init__(self) -> None:
        super().__init__()

    async def exec(self, session: Session) -> Result or None:
        return await self.preprocess(session)

    async def preprocess(self, session: Session) -> Result or None:
        if (not self.bot):
            raise AttributeError(
                f'Trigger {self.trigger}({self.__class__.__name__}) '
                'used before bot is assigned')
        if (self.use_help and session.args[0] == '帮助'):
            func_result: SessionResult = await session.reply(self.help)
            return func_result.result_type
        result: Result = await self.func(session)
        if (not result):
            return Result.SUCCESS
        else:
            return result

    async def func(self,
                   session: Session) -> Union[Result, None, SessionResult]:
        return super().func(session)
