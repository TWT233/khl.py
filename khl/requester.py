import asyncio
import logging
from typing import Union

from aiohttp import ClientSession

from .api_list import _Req
from .cert import Cert
from .interface import AsyncRunnable

log = logging.getLogger(__name__)

API = f'https://www.kaiheila.cn/api/v3'


class HTTPRequester(AsyncRunnable):
    def __init__(self, cert: Cert):
        self._cert = cert
        self._cs: ClientSession = ClientSession(loop=self.loop)

    def __del__(self):
        asyncio.get_event_loop().run_until_complete(self._cs.close())

    async def request(self, method: str, route: str, **params) -> Union[dict, list]:
        headers = params.pop('headers', {})
        headers['Authorization'] = f'Bot {self._cert.token}'
        params['headers'] = headers

        async with self._cs.request(method, f'{API}/{route}', **params) as res:
            log.debug(f'req: {method} {route}: {params}')
            rsp = await res.json()
            if rsp['code'] != 0:
                log.error(f'req failed: {rsp}, req: {method} {route}: {params}')
            else:
                log.debug(f'req done: {rsp}')
            return rsp['data']

    async def exec_req(self, r: _Req):
        return await self.request(r.method, r.route, **r.params)
