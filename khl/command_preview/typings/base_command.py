from abc import ABC, abstractmethod
from .types import BaseSession, CommandType
from khl.Message import BaseMsg
from typing import Any, Sequence, overload

from khl.Bot import Bot


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

    @abstractmethod
    @overload
    async def execute(self, command_str: str, arg_list: Sequence[str],
                      msg: BaseMsg) -> Any:
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
    def run_func(self, session: BaseSession) -> Any:
        """
        docstring
        """
        raise NotImplementedError

    @abstractmethod
    def func(self, session: BaseSession) -> Any:
        """
        docstring
        """
        raise NotImplementedError

    @property
    def bot(self):
        return self.__bot

    @bot.setter
    def set_bot(self, bot: Bot):
        # if (not isinstance(bot, Bot)):
        #     raise TypeError(
        #         'Trying to assign a non-bot instance!')
        self.__bot = bot

    @property
    def type(self):
        return self._type
