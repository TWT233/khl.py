import asyncio
import json
import time
import zlib

from aiohttp import ClientSession, web, ClientResponse

from .. import BaseClient, Cert


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
        self.recv = []
        self.sn_dup_map = {}

    async def send(self, url: str, data) -> ClientResponse:
        headers = {
            'Authorization': f'Bot {self.cert.token}',
            'Content-type': 'application/json'
        }
        async with self.cs.post(url, headers=headers, json=data) as res:
            await res.read()
            return res

    def on_recv_append(self, callback):
        self.recv.append(callback)
        pass

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
        sn = req['sn']
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
                d = req_json['d']
                if d['type'] == 1:
                    for i in self.recv:
                        await asyncio.ensure_future(i(d))
                if d['type'] == 255:
                    if d['channel_type'] == 'WEBHOOK_CHALLENGE':
                        return web.json_response({'challenge': d['challenge']})

            return web.Response()

        self.app.router.add_post(self.route, on_recv)

        async def on_shutdown(app):
            await self.cs.close()

        self.app.on_shutdown.append(on_shutdown)

    def run(self):
        self.__init_app()
        web.run_app(self.app, port=self.port)
