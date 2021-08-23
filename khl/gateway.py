import asyncio

from .receiver import Receiver
from .requester import HTTPRequester


class Gateway:
    _out: HTTPRequester
    _in: Receiver

    def __init__(self, requester: HTTPRequester, receiver: Receiver):
        self._out = requester
        self._in = receiver

    async def run(self, in_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        await self._in.run(in_queue, loop)
