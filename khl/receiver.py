import asyncio
import json
import logging
import time
import zlib
from abc import ABC, abstractmethod
from typing import Dict

from aiohttp import ClientWebSocketResponse, ClientSession, web

from .interface import AsyncRunnable
from .cert import Cert

log = logging.getLogger(__name__)

API = f'https://www.kaiheila.cn/api/v3'


class Receiver(AsyncRunnable, ABC):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @property
    def type(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def run(self, pkg_queue: asyncio.Queue):
        raise NotImplementedError


class WebsocketReceiver(Receiver):

    def __init__(self, cert: Cert, compress: bool = True):
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
        data = self.compress and zlib.decompress(data) or data
        data = json.loads(str(data, encoding='utf-8'))
        return data

    async def run(self, pkg_queue: asyncio.Queue):
        async with ClientSession(loop=self.loop) as cs:
            headers = {
                'Authorization': f'Bot {self._cert.token}',
                'Content-type': 'application/json'
            }
            params = {'compress': self.compress and 1 or 0}
            async with cs.get(f"{API}/gateway/index",
                              headers=headers,
                              params=params) as res:
                res_json = await res.json()
                if res_json['code'] != 0:
                    log.error(f'error getting gateway: {res_json}')
                    return

                self._RAW_GATEWAY = res_json['data']['url']

            async with cs.ws_connect(self._RAW_GATEWAY) as ws_conn:
                asyncio.ensure_future(self.heartbeat(ws_conn), loop=self.loop)

                async for raw in ws_conn:
                    try:
                        raw_pkg: Dict = self.__raw_to_pkg(raw.data)
                    except Exception as e:
                        log.error(e)
                        return
                    if raw_pkg['s'] == 0:
                        log.debug(f'upcoming raw_pkg: {raw_pkg}')
                        self._NEWEST_SN = raw_pkg['sn']
                        event = raw_pkg['d']
                        await pkg_queue.put(event)


class WebhookReceiver(Receiver):
    def __init__(self, cert: Cert, *, port=5000, route='/khl-wh', compress: bool = True):
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
        data = self.compress and zlib.decompress(data) or data
        data = json.loads(str(data, encoding='utf-8'))
        return ('encrypt' in data.keys()) and json.loads(self._cert.decrypt(data['encrypt'])) or data

    def __is_pkg_dup(self, req: dict) -> bool:
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

    async def run(self, pkg_queue: asyncio.Queue):
        async def on_recv(request: web.Request):
            raw_pkg: Dict = self.__raw_to_pkg(await request.read())
            assert raw_pkg
            assert raw_pkg['d']['verify_token'] == self._cert.verify_token

            if self.__is_pkg_dup(raw_pkg):
                return web.Response()

            if raw_pkg['s'] == 0:
                log.debug(f'upcoming raw_pkg: {raw_pkg}')
                pkg = raw_pkg['d']
                if pkg['type'] == 255 and pkg['channel_type'] == 'WEBHOOK_CHALLENGE':
                    return web.json_response({'challenge': pkg['challenge']})
                await pkg_queue.put(pkg)

            return web.Response()

        self.app.router.add_post(self.route, on_recv)

        async def on_shutdown(app):
            await self.cs.close()

        self.app.on_shutdown.append(on_shutdown)

        runner = web.AppRunner(self.app, access_log_class=None)
        await runner.setup()  # runner use its own loop, can not be set
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()

        while True:
            await asyncio.sleep(3600)  # sleep forever
