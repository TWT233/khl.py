from typing import Union, Callable, Coroutine, Any

from khl import Message, User

TypeRule = Callable[[Message], Union[bool, Coroutine[Any, Any, bool]]]


class Rule:
    """check if the msg fulfills some condition"""

    @staticmethod
    def is_bot_mentioned(bot) -> TypeRule:
        """:return: a Rule that checks if the bot is mentioned"""

        async def rule(msg: Message) -> bool:
            return (await bot.fetch_me()).id in msg.extra.get('mention')

        return rule

    @staticmethod
    def is_user_mentioned(user: User) -> TypeRule:
        """:return: a Rule that checks if the user is mentioned"""

        def rule(msg: Message) -> bool:
            return user.id in msg.extra.get('mention')

        return rule

    @staticmethod
    def is_mention_all(msg: Message) -> bool:
        """:return: a Rule that checks if the msg mentioned all members"""
        return msg.extra.get('mention_all', None) is not None

    @staticmethod
    def is_not_bot(msg: Message) -> bool:
        """:return: a Rule that check if the msg belong non bot"""
        return not msg.author.bot
