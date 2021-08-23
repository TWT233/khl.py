import asyncio
import logging
from typing import Union

from aiohttp import ClientSession

from .cert import Cert

log = logging.getLogger(__name__)

API = f'https://www.kaiheila.cn/api/v3'


class HTTPRequester:
    def __init__(self, cert: Cert):
        self._cert = cert
        self._cs: ClientSession = ClientSession()

    def __del__(self):
        asyncio.get_event_loop().run_until_complete(self._cs.close())

    async def request(self, method: str, route: str, **kwargs) -> Union[dict, list]:
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bot {self._cert.token}'
        kwargs['headers'] = headers

        async with self._cs.request(method, f'{API}/{route}', **kwargs) as res:
            rsp = await res.json()
            log_str = f'[{route}]({kwargs})->({rsp})'
            if rsp['code'] != 0:
                log.error(f'req failed: {log_str}')
            else:
                log.debug(f'req done: {log_str}')
            return rsp['data']
