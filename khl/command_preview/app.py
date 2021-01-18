from .typings.base_command import BaseCommand
from .session import Session
from .typings.types import BaseSession, ResultType, SessionResult
from .menu import MenuCommand

from khl.Message import Msg
from collections.abc import Sequence
from types import Union, overload


class AppCommand(BaseCommand):
    intro: str
    parent: MenuCommand or None

    def __init__(self) -> None:
        super().__init__()

    @overload
    async def execute(self, command_str: str, arg_list: Sequence[str],
                      msg: Msg) -> ResultType or None:
        return await self.run_func(Session(
            self,
            command_str,
            arg_list,
            msg,
        ))

    async def execute(self, session: Session) -> ResultType or None:
        return await self.run_func(session)

    async def run_func(self, session: BaseSession) -> ResultType or None:
        if (not self.bot):
            raise AttributeError(
                f'Trigger {self.trigger}({self.__class__.__name__}) '
                'used before bot is assigned')
        if (self.use_help and session.args[0] == '帮助'):
            await session.reply(self.help)
            return ResultType.HELP
        result: Union[ResultType, None,
                      SessionResult] = await self.func(session)
        if (not result):
            return ResultType.SUCCESS
        elif isinstance(result, SessionResult):
            return result.result_type
        else:
            return result

    async def func(
            self,
            session: BaseSession) -> Union[ResultType, None, SessionResult]:
        return super().func(session)
