"""
deprecated
"""

import asyncio


class Command:
    """
    Command class, used in Bot
    """
    def __init__(self, func, name: str):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError('handler must be a coroutine.')
        self.handler = func

        self.name = name = name or func.__name__
        if not isinstance(name, str):
            raise TypeError('Name of a command must be a string.')

    @staticmethod
    def command(name: str):
        """
        decorator to wrap a func into a Command

        :param name: the name of a Command, also used to trigger Command
        :return: wrapped Command
        """
        def decorator(func):
            return Command(func, name)

        return decorator
