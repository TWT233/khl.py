import asyncio

from .receiver import Receiver
from .requester import HTTPRequester


class Gateway:
    """
    Component which deals with network connection and package send/receive

    reminder: this is not AsyncRunnable cuz gateway dose not have its own tasks, only pass loop to _in/_out
    """
    _out: HTTPRequester
    _in: Receiver

    def __init__(self, requester: HTTPRequester, receiver: Receiver):
        self._out = requester
        self._in = receiver

    async def run(self, in_queue: asyncio.Queue):
        await self._in.run(in_queue)
