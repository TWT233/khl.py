from abc import ABC
import asyncio
from khl.command.base import BaseCommand
from khl.command import Session


class App(BaseCommand):
    intro: str

    def __init__(self) -> None:
        super().__init__()

    async def exec(self, session: Session) -> None:
        pass

    async def __run(self) -> None:
        pass

    async def func(self, session: Session):
        return super().func(session)
