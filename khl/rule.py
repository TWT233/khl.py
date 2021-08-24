from abc import ABC
from khl import Msg


class Rule(ABC):
    @staticmethod
    def at_me():
        async def f(msg: Msg, *args):
            bot_id = await msg.ctx.bot.id()
            return bot_id in msg.extra.get('mention')

        return f

    @staticmethod
    def at_all():
        async def f(msg: Msg, *args):
            return bool(msg.extra.get('mention_all'))

        return f

    @staticmethod
    def on_channel(name: str):
        async def f(msg: Msg, *args):
            return name == msg.ctx.channel.name

        return f
