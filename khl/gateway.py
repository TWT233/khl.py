import asyncio
from abc import ABC

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


class Requestable(ABC):
    """
    Classes that can use a `Gateway` to communicate with khl server.

    For example:
        `Message`: can use msg.reply() to send a reply to khl

        `Guild`: guild.get_roles() to fetch role list from khl
    """
    gate: Gateway
