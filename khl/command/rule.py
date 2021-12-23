from typing import Union, Callable, Coroutine, Any

from khl import Message, User

TypeRule = Callable[[Message], Union[bool, Coroutine[Any, Any, bool]]]


class Rule:
    @staticmethod
    def is_bot_mentioned(bot) -> TypeRule:
        async def rule(msg: Message) -> bool:
            return (await bot.fetch_me()).id in msg.extra.get('mention')

        return rule

    @staticmethod
    def is_user_mentioned(user: User) -> TypeRule:
        def rule(msg: Message) -> bool:
            return user.id in msg.extra.get('mention')

        return rule

    @staticmethod
    def is_mention_all(msg: Message) -> bool:
        return msg.extra.get('mention_all', None) is not None
