from abc import ABC, abstractmethod
from khl.command.session import Session
from khl.Bot import Bot


class BaseCommand(ABC):
    trigger: str
    help: str
    _bot: Bot

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
        return self.bot

    @bot.setter
    def bot(self, bot):
        if (not isinstance(bot, Bot)):
            raise TypeError(
                'Trying to assign none bot instance to bot attribute!')
        self._bot = bot
