from abc import ABC, abstractmethod
from khl.bot import Bot
from khl.message import Message


class Rule(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def at_all(self):
        raise NotImplementedError


class CommandRule(Rule):
    bot: Bot

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    def at_me(self):
        async def func(msg: Message, *args, **kwargs):
            bot_user = await self.bot.fetch_me()
            bot_id = bot_user.id
            return bot_id in msg.extra.get('mention')

        return func

    def at_all(self):
        def func(msg: Message, *args, **kwargs):
            return bool(msg.extra.get('mention_all'))

        return func
