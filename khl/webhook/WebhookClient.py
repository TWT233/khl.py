import json
import zlib

import asyncio
from aiohttp import ClientSession, web

from .. import BaseClient
from . import Cert


class WebhookClient(BaseClient):

    def __init__(self, *, port=5000, route='/khl-wh', compress: bool = True, cert: Cert):
        super().__init__(port)
        self.type = 'webhook'
        self.route = route
        self.cs = ClientSession()
        self.app = web.Application()
        self.cert = cert
        self.compress = compress
        self.recv = []

    async def send(self, url: str, data):
        headers = {'Authorization': f'Bot {self.cert.token}', 'Content-type': 'application/json'}
        async with self.cs.post(url, headers=headers, json=data) as res:
            return res

    def on_recv_append(self, callback):
        self.recv.append(callback)
        pass

    def data_to_json(self, data: bytes):
        data = self.compress and zlib.decompress(data) or data
        data = json.loads(str(data, encoding='utf-8'))
        return ('encrypt' in data.keys()) and json.loads(self.cert.decrypt(data['encrypt'])) or data

    def init_app(self):
        async def on_recv(request: web.Request):
            req_json = self.data_to_json(await request.read())
            assert req_json
            assert req_json['d']['verify_token'] == self.cert.verify_token

            if req_json['s'] == 0:
                d = req_json['d']
                if d['type'] == 1:
                    for i in self.recv:
                        asyncio.ensure_future(i(d))
                if d['type'] == 255:
                    if d['channel_type'] == 'WEBHOOK_CHALLENGE':
                        return web.json_response({'challenge': d['challenge']})

            return web.Response(status=200)

        self.app.router.add_post(self.route, on_recv)

        async def on_shutdown(app):
            await self.cs.close()

        self.app.on_shutdown.append(on_shutdown)

    def run(self):
        self.init_app()
        web.run_app(self.app, port=self.port)
