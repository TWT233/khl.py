from khl.command.types import Result
from khl.command.session import Session
from khl.command.base import BaseCommand
from khl.command.menu import MenuCommand


class AppCommand(BaseCommand):
    intro: str
    parent: MenuCommand or None

    def __init__(self) -> None:
        super().__init__()

    async def exec(self, session: Session) -> Result or None:
        return await self.__run(session)

    async def __run(self, session: Session) -> Result or None:
        if (not self.bot):
            raise AttributeError(
                f'Trigger {self.trigger}({self.__class__.__name__}) '
                'used before bot is assigned')
        if (self.use_help and session.args[0] == '帮助'):
            return session.reply(self.help)
        result: Result = await self.func(session)
        if (not result):
            return Result.SUCCESS
        else:
            return result

    async def func(self, session: Session):
        return super().func(session)
