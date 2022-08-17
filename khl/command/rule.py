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
    def is_mention_all() -> TypeRule:
        """:return: a Rule that checks if the msg mentioned all members"""

        def rule(msg: Message) -> bool:
            return msg.extra.get('mention_all', None) is not None

        return rule

    @staticmethod
    def is_not_bot() -> TypeRule:
        """:return: a Rule that check if the msg belong non bot"""

        def rule(msg: Message) -> bool:
            return not msg.author.bot

        return rule
