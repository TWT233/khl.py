import asyncio
import logging
import time
import zlib
from abc import ABC, abstractmethod
from typing import Dict

from aiohttp import ClientWebSocketResponse, ClientSession, web, WSMessage

from .cert import Cert
from .interface import AsyncRunnable

log = logging.getLogger(__name__)

API = 'https://www.kaiheila.cn/api/v3'


class Receiver(AsyncRunnable, ABC):
    """
    1. receive raw data from khl server
    2. decrypt & parse raw data into pkg
    3. put pkg into the pkg_queue() for others to use
    """
    _queue: asyncio.Queue

    @property
    def type(self) -> str:
        """the network type used by the receiver"""
        raise NotImplementedError

    @property
    def pkg_queue(self) -> asyncio.Queue:
        """output port of the receiver"""
        return self._queue

    @pkg_queue.setter
    def pkg_queue(self, queue: asyncio.Queue):
        self._queue = queue

    @abstractmethod
    async def start(self):
        """run self"""
        raise NotImplementedError


class WebsocketReceiver(Receiver):
    """receive data in websocket mode"""

    def __init__(self, cert: Cert, compress: bool):
        super().__init__()
        self._cert = cert
        self.compress = compress

        self._NEWEST_SN = 0
        self._RAW_GATEWAY = ''

    @property
    def type(self) -> str:
        return 'websocket'

    async def heartbeat(self, ws_conn: ClientWebSocketResponse):
        """khl customized heartbeat scheme"""
        while True:
            try:
                await asyncio.sleep(26)
                await ws_conn.send_json({'s': 2, 'sn': self._NEWEST_SN})
            except ConnectionResetError:
                return
            except Exception as e:
                log.exception('error raised during websocket heartbeat',
                              exc_info=e)

    async def _get_gateway(self, cs: ClientSession):
        headers = {
            'Authorization': f'Bot {self._cert.token}',
            'Content-type': 'application/json'
        }
        params = {'compress': 1 if self.compress else 0}
        async with cs.get(f"{API}/gateway/index",
                          headers=headers,
                          params=params) as res:
            res_json = await res.json()
            if res_json['code'] != 0:
                log.error(f'getting gateway: {res_json}')
                return

            self._RAW_GATEWAY = res_json['data']['url']

    async def _connect_gateway_and_handle_msg(self, cs: ClientSession):
        async with cs.ws_connect(self._RAW_GATEWAY) as ws_conn:
            asyncio.ensure_future(self.heartbeat(ws_conn), loop=self.loop)

            log.info('[ init ] launched')
            try:
                async for raw in ws_conn:
                    raw: WSMessage
                    await self._handle_raw(raw)
            except Exception:
                log.exception(
                    'error raised during websocket receive, reconnect automatically'
                )

    async def start(self):
        async with ClientSession(loop=self.loop) as cs:
            while True:
                await self._get_gateway(cs)
                await self._connect_gateway_and_handle_msg(cs)

    async def _handle_raw(self, raw: WSMessage):
        try:
            data = raw.data
            data = zlib.decompress(data) if self.compress else data
            pkg: Dict = self._cert.decode_raw(data)
            log.debug(f'upcoming raw: {pkg}')
            if pkg['s'] != 0:
                return
            self._NEWEST_SN = pkg['sn']
            await self.pkg_queue.put(pkg['d'])
        except Exception as e:
            log.exception(e)


class WebhookReceiver(Receiver):
    """receive data in webhook mode"""

    def __init__(self, cert: Cert, *, port: int, route: str, compress: bool):
        super().__init__()
        self._cert = cert
        self.port = port
        self.route = route
        self.app = web.Application()
        self.compress = compress
        self.sn_dup_map = {}

    @property
    def type(self) -> str:
        return 'webhook'

    def _is_dup(self, req: dict) -> bool:
        sn = req.get('sn', None)
        if sn is None:
            return False
        current = time.time()
        if sn in self.sn_dup_map:
            if current - self.sn_dup_map[sn] <= 600:
                # 600 sec timed out
                return True
        self.sn_dup_map[sn] = current
        return False

    async def start(self):

        async def on_recv(request: web.Request):
            try:
                data = await request.read()
                data = zlib.decompress(data) if self.compress else data
                pkg: Dict = self._cert.decode_raw(data)
            except Exception as e:
                log.exception(e)
                return web.Response()

            if not pkg:  # empty pkg
                return web.Response()

            if pkg['d'][
                    'verify_token'] != self._cert.verify_token:  # check verify_token
                return web.Response()

            if self._is_dup(pkg):  # dup pkg
                return web.Response()

            if pkg['s'] == 0:
                pkg = pkg['d']
                if pkg['type'] == 255 and pkg[
                        'channel_type'] == 'WEBHOOK_CHALLENGE':
                    return web.json_response({'challenge': pkg['challenge']})
                await self.pkg_queue.put(pkg)

            return web.Response()

        self.app.router.add_post(self.route, on_recv)

        runner = web.AppRunner(self.app)
        await runner.setup()  # runner use its own loop, can not be set
        site = web.TCPSite(runner, '0.0.0.0', self.port)

        log.info('[ init ] launched')

        await site.start()

        while True:
            await asyncio.sleep(3600)  # sleep forever
