import asyncio
import logging
from typing import Dict, List, Callable

from .gateway import Gateway

log = logging.getLogger(__name__)


class Client:
    _gate: Gateway

    _handler_map: Dict[int, List[Callable]]
    _loop: asyncio.AbstractEventLoop

    def __init__(self, gate: Gateway):
        self._gate = gate

        self._handler_map = {}
        self._event_queue = asyncio.Queue()

    async def event_handler(self):
        pass
