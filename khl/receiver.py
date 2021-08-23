import asyncio
import json
import logging
import time
import zlib
from abc import ABC, abstractmethod

from aiohttp import ClientWebSocketResponse, ClientSession, web

from .cert import Cert
from .hardcoded import API_URL

log = logging.getLogger(__name__)


class Receiver(ABC):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    @property
    def type(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def run(self, event_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        raise NotImplementedError


class WebsocketReceiver(Receiver):

    def __init__(self, cert: Cert, compress: bool = True):
        super().__init__()
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

    def __pkg_to_req(self, data: bytes) -> dict:
        data = self.compress and zlib.decompress(data) or data
        data = json.loads(str(data, encoding='utf-8'))
        return data

    async def run(self, event_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        async with ClientSession() as cs:
            headers = {
                'Authorization': f'Bot {self._cert.token}',
                'Content-type': 'application/json'
            }
            params = {'compress': self.compress and 1 or 0}
            async with cs.get(f"{API_URL}/gateway/index",
                              headers=headers,
                              params=params) as res:
                res_json = await res.json()
                if res_json['code'] != 0:
                    log.error(f'error getting gateway: {res_json}')
                    return

                self._RAW_GATEWAY = res_json['data']['url']

            async with cs.ws_connect(self._RAW_GATEWAY) as ws_conn:
                asyncio.ensure_future(self.heartbeat(ws_conn), loop=loop)

                async for msg in ws_conn:
                    try:
                        req_json = self.__pkg_to_req(msg.data)
                    except Exception as e:
                        log.error(e)
                        return
                    if req_json['s'] == 0:
                        self._NEWEST_SN = req_json['sn']
                        event = req_json['d']
                        await event_queue.put(event)


class WebhookReceiver(Receiver):
    def __init__(self, cert: Cert, *, port=5000, route='/khl-wh', compress: bool = True):
        super().__init__()
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

    def __raw_2_req(self, data: bytes) -> dict:
        data = self.compress and zlib.decompress(data) or data
        data = json.loads(str(data, encoding='utf-8'))
        return ('encrypt' in data.keys()) and json.loads(self._cert.decrypt(data['encrypt'])) or data

    def __is_req_dup(self, req: dict) -> bool:
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

    async def run(self, event_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        async def on_recv(request: web.Request):
            req_json = self.__raw_2_req(await request.read())
            assert req_json
            assert req_json['d']['verify_token'] == self._cert.verify_token

            if self.__is_req_dup(req_json):
                return web.Response()

            if req_json['s'] == 0:
                event = req_json['d']
                if event['type'] == 255:
                    if event['channel_type'] == 'WEBHOOK_CHALLENGE':
                        return web.json_response(
                            {'challenge': event['challenge']})
                await event_queue.put(event)

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
