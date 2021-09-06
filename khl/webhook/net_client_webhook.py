import asyncio
from asyncio.events import AbstractEventLoop
import json
import logging
import time
import zlib

from aiohttp import ClientSession, web, ClientResponse

from ..net_client import BaseClient
from ..cert import Cert


class WebhookClient(BaseClient):
    """
    implements BaseClient with webhook protocol
    """
    def __init__(self,
                 *,
                 port=5000,
                 route='/khl-wh',
                 compress: bool = True,
                 cert: Cert):
        """
        :param port: port to set webhook server on
        :param route: route for your webhook server
        :param compress: enable data compress or not, enabled as default
        :param cert: used to auth and data decrypt/encrypt
        """
        super().__init__()
        self.type = 'webhook'
        self.port = port
        self.route = route
        self.cs = ClientSession()
        self.app = web.Application()
        self.cert = cert
        self.compress = compress
        self.event_queue = asyncio.Queue()
        self.sn_dup_map = {}

    def setup_event_loop(self, loop: AbstractEventLoop):
        self.event_queue = asyncio.Queue(loop=loop)

    def __raw_2_req(self, data: bytes) -> dict:
        """
        convert raw data to human-readable request data

        decompress and decrypt data(if configured with compress or encrypt)
        :param data: raw data
        :return human-readable request data
        """
        data = self.compress and zlib.decompress(data) or data
        data = json.loads(str(data, encoding='utf-8'))
        return ('encrypt' in data.keys()) and json.loads(
            self.cert.decrypt(data['encrypt'])) or data

    def __is_req_dup(self, req: dict) -> bool:
        """
        check if a req is dup
        """
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

    def __init_app(self):
        """
        init aiohttp app
        """
        async def on_recv(request: web.Request):
            req_json = self.__raw_2_req(await request.read())
            assert req_json
            assert req_json['d']['verify_token'] == self.cert.verify_token

            if self.__is_req_dup(req_json):
                return web.Response()

            if req_json['s'] == 0:
                event = req_json['d']
                if event['type'] == 255:
                    if event['channel_type'] == 'WEBHOOK_CHALLENGE':
                        return web.json_response(
                            {'challenge': event['challenge']})
                await self.event_queue.put(event)

            return web.Response()

        self.app.router.add_post(self.route, on_recv)

        async def on_shutdown(app):
            await self.cs.close()

        self.app.on_shutdown.append(on_shutdown)

    async def run(self):
        self.__init_app()
        runner = web.AppRunner(self.app, access_log_class=_AccessLogger)
        try:
            await runner.setup()
        except Exception as e:
            logging.exception('app runner setup error: %s', e)
            runner._server = runner._make_server()
        site = web.TCPSite(runner, '0.0.0.0', self.port)
        await site.start()

        while True:
            await asyncio.sleep(3600)  # sleep forever


from aiohttp.abc import AbstractAccessLogger


class _AccessLogger(AbstractAccessLogger):
    def log(self, request, response, time):
        self.logger.debug(f'{request.remote} '
                          f'"{request.method} {request.path} '
                          f'done in {time}s: {response.status}')
