from typing import Coroutine


async def wrap_if_coro(call):
    """if call is a coroutine, wrap it in await"""
    if isinstance(call, Coroutine):
        return await call
    return call
