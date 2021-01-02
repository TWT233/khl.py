import asyncio


class Command:
    def __init__(self, func, name: str):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError('handler must be a coroutine.')
        self.handler = func

        self.name = name = name or func.__name__
        if not isinstance(name, str):
            raise TypeError('Name of a command must be a string.')

    @staticmethod
    def command(name: str):
        def decorator(func):
            return Command(func, name)

        return decorator
