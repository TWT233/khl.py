from typing import Sequence, Union, overload
from .typings.base_command import BaseCommand
from .session import Session
from .typings.types import BaseSession
from .menu import MenuCommand

from khl.message import Msg


class AppCommand(BaseCommand):
    intro: str
    parent: MenuCommand or None

    def __init__(self) -> None:
        super().__init__()

    @overload
    async def execute(self, command_str: str, args: Sequence[str],
                      msg: Msg) -> BaseSession.ResultTypes or None:
        return await self.run_func(Session(
            self,
            command_str,
            args,
            msg,
        ))

    async def execute(self,
                      session: Session) -> BaseSession.ResultTypes or None:
        return await self.run_func(session)

    async def run_func(
            self, session: BaseSession) -> BaseSession.ResultTypes or None:
        if not self.bot:
            raise AttributeError(
                f'Trigger {self.trigger}({self.__class__.__name__}) '
                'used before bot is assigned')
        if session.args and self.use_help and session.args[0] == '帮助':
            await session.reply(self.help)
            return BaseSession.ResultTypes.HELP
        result: Union[BaseSession.ResultTypes, None,
                      BaseSession] = await self.func(session)
        if not result:
            return BaseSession.ResultTypes.SUCCESS
        elif isinstance(result, BaseSession):
            return result.result_type
        else:
            return result

    async def func(
        self, session: BaseSession
    ) -> Union[BaseSession, BaseSession.ResultTypes, None]:
        return None
