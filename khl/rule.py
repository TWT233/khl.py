from abc import ABC, abstractmethod
from .bot import Bot
from .message import Message

import asyncio


class Rule(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def at_me(self, *args, **kwargs) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def at_all(self, *args, **kwargs) -> bool:
        raise NotImplementedError


class MessageRule(Rule, Bot):
    bot: Bot

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    async def at_me(self, msg: Message, *args, **kwargs) -> bool:
        # loop = asyncio.get_event_loop()
        # bot_user = loop.run_until_complete(self.bot.fetch_me())
        # #Error: This event loop is already running

        bot_user = await self.bot.fetch_me()
        bot_id = bot_user.id
        return bot_id in msg.extra.get('mention')

    async def at_all(self, msg: Message, *args, **kwargs) -> bool:
        return bool(msg.extra.get('mention_all'))
