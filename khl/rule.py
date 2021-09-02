from typing import Callable, Coroutine
from abc import ABC, abstractmethod
from khl import Msg


class Rule(ABC):
    @abstractmethod
    def at_me(*args, **kwargs) -> (Callable[..., Coroutine]):
        raise NotImplementedError

    @abstractmethod
    def at_all(*args, **kwargs) -> (Callable[..., Coroutine]):
        raise NotImplementedError

    @abstractmethod
    def on_channel(self, name: str, *args, **kwargs) -> (Callable[..., Coroutine]):
        raise NotImplementedError


class MessageRule(Rule):
    """
    can used in all message

    @bot.command(name='hello', rule=MessageRule.at_me())
    async def examples(msg: TextMsg, *args):
        await msg.reply(f'hello')
    """

    def at_me(*args, **kwargs) -> (Callable[..., Coroutine]):
        async def f(msg: Msg, *args) -> bool:
            bot_id = await msg.ctx.bot.id()
            return bot_id in msg.extra.get('mention')

        return f

    def at_all(*args, **kwargs) -> (Callable[..., Coroutine]):
        async def f(msg: Msg, *args) -> bool:
            return bool(msg.extra.get('mention_all'))

        return f

    def on_channel(self, name: str, *args, **kwargs) -> (Callable[..., Coroutine]):
        async def f(msg: Msg, *args) -> bool:
            return name == msg.ctx.channel.name

        return f
