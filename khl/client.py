import asyncio
import inspect
import logging
from typing import Dict, List, Callable

from . import api
from .channel import public_channel_factory, PublicChannel
from .gateway import Gateway, Requestable
from .guild import Guild
from .interface import AsyncRunnable, MessageTypes
from .message import RawMessage, Event, PublicMessage, PrivateMessage
from .user import User

log = logging.getLogger(__name__)


class Client(Requestable, AsyncRunnable):
    """
    The bridge between khl.py internal components and khl server.

    Translates network package into khl.py concepts/object for internal to use.

    reminder: Client.loop only used to run handle_event() and registered handlers.
    """
    _handler_map: Dict[MessageTypes, List[Callable]]

    def __init__(self, gate: Gateway):
        self.gate = gate

        self._handler_map = {}
        self._pkg_queue = asyncio.Queue()

    def register(self, type: MessageTypes, handler: Callable):
        if not asyncio.iscoroutinefunction(handler):
            raise TypeError('handler must be a coroutine.')

        params = list(inspect.signature(handler).parameters.items())
        if len(params) != 1 or not issubclass(params[0][1].annotation, RawMessage):
            raise TypeError('handler must have one and only one param, and the param inherits RawMessage')

        if type not in self._handler_map:
            self._handler_map[type] = []
        self._handler_map[type].append(handler)

    async def handle_pkg(self):
        """
        Pop `pkg` from `event_queue`,
        spawn `msg` according to `pkg`,
        pass `msg` to corresponding handlers defined in `_handler_map`
        """
        while True:
            pkg: Dict = await self._pkg_queue.get()
            log.debug(f'upcoming pkg: {pkg}')

            try:
                msg = self._make_msg(pkg)
                self._dispatch_msg(msg)
            except Exception as e:
                log.exception(e)

            self._pkg_queue.task_done()

    def _make_msg(self, pkg: Dict):
        if pkg.get('type') == MessageTypes.SYS.value:
            msg = Event(**pkg)
        else:
            msg = self._make_channel_msg(pkg)
        return msg

    def _make_channel_msg(self, pkg):
        msg = None
        channel_type = pkg.get('channel_type')
        if channel_type == 'GROUP':
            msg = PublicMessage(**pkg, _gate_=self.gate)
        elif channel_type == 'PERSON':
            msg = PrivateMessage(**pkg, _gate_=self.gate)
        else:
            log.error(f'can not make msg from pkg: {pkg}')
        return msg

    def _dispatch_msg(self, msg):
        if not msg:
            return
        if msg.type in self._handler_map and self._handler_map[msg.type]:
            for handler in self._handler_map[msg.type]:
                asyncio.ensure_future(handler(msg), loop=self.loop)

    async def create_asset(self, file: str) -> str:
        """upload ``file`` to khl, and return the url to the file"""
        return (await self.gate.exec_req(api.Asset.create(file=open(file, 'rb'))))['url']

    async def fetch_me(self) -> User:
        """fetch detail of the ``User`` on the client"""
        return User(_gate_=self.gate, _lazy_loaded_=True, **(await self.gate.exec_req(api.User.me())))

    async def fetch_public_channel(self, channel_id: str) -> PublicChannel:
        """fetch details of a public channel from khl"""
        channel_data = await self.gate.exec_req(api.Channel.view(channel_id))
        return public_channel_factory(_gate_=self.gate, **channel_data)

    async def list_guild(self) -> List[Guild]:
        """list guilds which the client joined"""
        guilds_data = (await self.gate.exec_pagination_req(api.Guild.list()))
        return [Guild(_gate_=self.gate, _lazy_loaded_=True, **i) for i in guilds_data]

    async def run(self):
        await asyncio.gather(self.handle_pkg(), self.gate.run(self._pkg_queue), loop=self.loop)
