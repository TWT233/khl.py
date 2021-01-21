from .command import Command
from typing import Sequence, Union, overload

from .session import Session
from .menu import MenuCommand

from khl.message import Msg


class AppCommand(Command):
    intro: str
    parent: MenuCommand or None

    def __init__(self) -> None:
        super().__init__()

    @overload
    async def execute(self, command_str: str, args: Sequence[str],
                      msg: Msg) -> Session.ResultTypes or None:
        return await self.run_func(Session(
            self,
            command_str,
            args,
            msg,
        ))

    async def execute(self, session: Session) -> Session.ResultTypes or None:
        return await self.run_func(session)

    async def run_func(self, session: Session) -> Session.ResultTypes or None:
        if (not self.bot):
            raise AttributeError(
                f'Trigger {self.trigger}({self.__class__.__name__}) '
                'used before bot is assigned')
        if (session.args and self.use_help and session.args[0] == '帮助'):
            await session.reply(self.help)
            return Session.ResultTypes.HELP
        result: Union[Session.ResultTypes, None,
                      Session] = await self.func(session)
        if (not result):
            return Session.ResultTypes.SUCCESS
        elif isinstance(result, Session):
            return result.result_type
        else:
            return result

    async def func(
            self,
            session: Session) -> Union[Session, Session.ResultTypes, None]:
        return None
