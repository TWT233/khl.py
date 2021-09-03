import asyncio
import logging
from typing import Dict, List, Callable

from .gateway import Gateway
from .interface import AsyncRunnable
from .gateway import Requestable
from .message import RawMessage, Event, ChannelMessage, PrivateMessage

log = logging.getLogger(__name__)


class Client(Requestable, AsyncRunnable):
    """
    The bridge between khl.py internal components and khl server.

    Translates network package into khl.py concepts/object for internal to use.

    reminder: Client.loop only used to run handle_event() and registered handlers.
    """
    _handler_map: Dict[int, List[Callable]]

    def __init__(self, gate: Gateway):
        self._gate = gate

        self._handler_map = {}
        self._pkg_queue = asyncio.Queue()

    async def handle_pkg(self):
        """
        Pop `pkg` from `event_queue`,
        spawn `msg` according to `pkg`,
        pass `msg` to corresponding handlers defined in `_handler_map`
        """
        while True:
            pkg: Dict = await self._pkg_queue.get()
            log.debug(f'upcoming pkg: {pkg}')

            msg: RawMessage
            if pkg['type'] == RawMessage.Types.SYS.value:
                msg = Event(**pkg)
            else:
                if pkg['channel_type'] == 'GROUP':
                    msg = ChannelMessage(**pkg, _gate_=self.gate)
                elif pkg['channel_type'] == 'PERSON':
                    msg = PrivateMessage(**pkg, _gate_=self.gate)
                else:
                    log.error(f'can not spawn msg from pkg: {pkg}')
                    self._pkg_queue.task_done()
                    continue

            if msg.type in self._handler_map and self._handler_map[msg.type]:
                for handler in self._handler_map[msg.type]:
                    asyncio.ensure_future(handler(msg), loop=self.loop)

            self._pkg_queue.task_done()

    async def run(self):
        asyncio.ensure_future(self.handle_pkg(), loop=self.loop)
        await self.gate.run(self._pkg_queue)
