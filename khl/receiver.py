import asyncio
import json
import logging
import time
import zlib
from abc import ABC, abstractmethod
from typing import Dict

from aiohttp import ClientWebSocketResponse, ClientSession, web, WSMessage

from .cert import Cert
from .interface import AsyncRunnable

log = logging.getLogger(__name__)

API = f'https://www.kaiheila.cn/api/v3'


class Receiver(AsyncRunnable, ABC):
    _queue: asyncio.Queue

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @property
    def type(self) -> str:
        raise NotImplementedError

    @property
    def pkg_queue(self) -> asyncio.Queue:
        return self._queue

    @pkg_queue.setter
    def pkg_queue(self, queue: asyncio.Queue):
        self._queue = queue

    @abstractmethod
    async def run(self):
        raise NotImplementedError


class WebsocketReceiver(Receiver):

    def __init__(self, cert: Cert, compress: bool):
        self._cert = cert
        self.compress = compress

        self._NEWEST_SN = 0
        self._RAW_GATEWAY = ''

    @property
    def type(self) -> str:
        return 'websocket'

    async def heartbeat(self, ws_conn: ClientWebSocketResponse):
        while True:
            await asyncio.sleep(26)
            await ws_conn.send_json({'s': 2, 'sn': self._NEWEST_SN})

    def __raw_to_pkg(self, data: bytes) -> dict:
        data = zlib.decompress(data) if self.compress else data
        data = json.loads(str(data, encoding='utf-8'))
        return data

    async def run(self):
        async with ClientSession(loop=self.loop) as cs:
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

            async with cs.ws_connect(self._RAW_GATEWAY) as ws_conn:
                asyncio.ensure_future(self.heartbeat(ws_conn), loop=self.loop)

                log.info('[ init ] launched')

                async for raw in ws_conn:
                    try:
                        raw: WSMessage
                        pkg: Dict = self.__raw_to_pkg(raw.data)
                        log.debug(f'upcoming raw: {pkg}')
                    except Exception as e:
                        log.exception(e)
                        continue

                    if pkg['s'] == 0:
                        self._NEWEST_SN = pkg['sn']
                        event = pkg['d']
                        await self.pkg_queue.put(event)


class WebhookReceiver(Receiver):
    def __init__(self, cert: Cert, *, port: int, route: str, compress: bool):
        self._cert = cert
        self.port = port
        self.route = route
        self.cs = ClientSession()
        self.app = web.Application()
        self.compress = compress
        self.sn_dup_map = {}

    @property
    def type(self) -> str:
        return 'webhook'

    def __raw_to_pkg(self, data: bytes) -> dict:
        data = zlib.decompress(data) if self.compress else data
        data = json.loads(str(data, encoding='utf-8'))
        return ('encrypt' in data.keys()) and json.loads(self._cert.decrypt(data['encrypt'])) or data

    def __is_pkg_dup(self, req: dict) -> bool:
        # TODO: need a recycle count down ring
        sn = req.get('sn', None)
        if not sn:
            return False
        current = time.time()
        if sn in self.sn_dup_map.keys():
            if current - self.sn_dup_map[sn] <= 600:
                # 600 sec timed out
                return True
        self.sn_dup_map[sn] = current
        return False

    async def run(self):
        async def on_recv(request: web.Request):
            try:
                pkg: Dict = self.__raw_to_pkg(await request.read())
            except Exception as e:
                log.exception(e)
                return web.Response()

            if not pkg or pkg['d']['verify_token'] != self._cert.verify_token:
                # empty pkg or verify_token check failed
                return web.Response()

            if self.__is_pkg_dup(pkg):
                # dupe pkg
                return web.Response()

            if pkg['s'] == 0:
                pkg = pkg['d']
                if pkg['type'] == 255 and pkg['channel_type'] == 'WEBHOOK_CHALLENGE':
                    return web.json_response({'challenge': pkg['challenge']})
                await self.pkg_queue.put(pkg)

            return web.Response()

        self.app.router.add_post(self.route, on_recv)

        async def on_shutdown(app):
            await self.cs.close()

        self.app.on_shutdown.append(on_shutdown)

        runner = web.AppRunner(self.app, access_log_class=None)
        await runner.setup()  # runner use its own loop, can not be set
        site = web.TCPSite(runner, '0.0.0.0', self.port)

        log.info('[ init ] launched')

        await site.start()

        while True:
            await asyncio.sleep(3600)  # sleep forever
