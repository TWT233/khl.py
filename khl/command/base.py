from abc import ABC, abstractmethod
from khl.command.types import CommandType

from khl.Bot import Bot
from khl.command import Session


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
    def exec(self, session: Session):
        """
        docstring
        """
        raise NotImplementedError

    @abstractmethod
    def __run(self, session: Session):
        """
        docstring
        """
        raise NotImplementedError

    @abstractmethod
    def func(self, session: Session):
        """
        docstring
        """
        raise NotImplementedError

    @property
    def bot(self):
        return self.__bot

    @bot.setter
    def set_bot(self, bot):
        if (not isinstance(bot, Bot)):
            raise TypeError(
                'Trying to assign none bot instance to bot attribute!')
        self.__bot = bot

    @property
    def type(self):
        return self._type
