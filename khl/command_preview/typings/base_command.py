from abc import ABC, abstractmethod
from .types import BaseSession, CommandType
from khl.message import Msg
from typing import Any, Sequence, overload

from khl.bot import Bot


class BaseCommand(ABC):
    trigger: str
    help: str
    __bot: Bot
    _type: CommandType

    use_help: bool = True
    with_reply: bool = True
    with_mention: bool = True

    def __init__(self) -> None:
        self.name = self.__class__.__name__

    @overload
    @abstractmethod
    async def execute(self, command_str: str, args: Sequence[str],
                      msg: Msg) -> Any:
        """
        docstring
        """
        raise NotImplementedError

    @abstractmethod
    async def execute(self, session: BaseSession) -> Any:
        """
        docstring
        """
        raise NotImplementedError

    @abstractmethod
    async def run_func(self, session: BaseSession) -> Any:
        """
        docstring
        """
        raise NotImplementedError

    @abstractmethod
    async def func(self, session: BaseSession) -> Any:
        """
        docstring
        """
        raise NotImplementedError

    @property
    def bot(self):
        return self.__bot

    def set_bot(self, bot):
        self.__bot = bot

    @property
    def type(self):
        return self._type
