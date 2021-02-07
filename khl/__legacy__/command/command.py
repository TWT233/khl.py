from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Sequence, TYPE_CHECKING, overload
if TYPE_CHECKING:
    from .session import Session
    from khl.message import Msg


class Command(ABC):
    class Types(Enum):
        MENU = 'MENU'
        APP = 'APP'

    trigger: str
    help: str
    __bot: Any

    use_help: bool = True
    with_reply: bool = True
    with_mention: bool = True

    def __init__(self) -> None:
        self.name = self.__class__.__name__

    @overload
    @abstractmethod
    async def execute(self, command_str: str, args: Sequence[str],
                      msg: 'Msg') -> Any:
        """
        docstring
        """
        raise NotImplementedError

    @abstractmethod
    async def execute(self, session: 'Session') -> Any:
        """
        docstring
        """
        raise NotImplementedError

    @abstractmethod
    async def run_func(self, session: 'Session') -> Any:
        """
        docstring
        """
        raise NotImplementedError

    @abstractmethod
    async def func(self, session: 'Session') -> Any:
        """
        docstring
        """
        raise NotImplementedError

    @property
    def bot(self):
        return self.__bot

    def set_bot(self, bot: Any):
        self.__bot = bot
