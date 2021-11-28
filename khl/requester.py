import asyncio
import logging
from typing import Union, List

from aiohttp import ClientSession

from .api import _Req
from .cert import Cert

log = logging.getLogger(__name__)

API = f'https://www.kaiheila.cn/api/v3'


class HTTPRequester:
    def __init__(self, cert: Cert):
        self._cert = cert
        self._cs: ClientSession = ClientSession()

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
                raise HTTPRequester.APIRequestFailed(method, route, params, rsp['code'], rsp['message'])
            else:
                log.debug(f'req done: {rsp}')
            return rsp['data']

    async def exec_req(self, r: _Req):
        return await self.request(r.method, r.route, **r.params)

    async def exec_pagination_req(self, r: _Req, *, begin_page: int = 1, end_page: int = None,
                                  page_size: int = 50, sort: str = '') -> List:
        """
        exec pagination requests, iter from ``begin_page`` to the ``end_page``, ``end_page=None`` means to the end

        1. get a req, inject the params
        2. req and receive the result
        3. unwrap the result, append result, fresh pagination params
        """
        ret = []
        current_page = begin_page
        while end_page is None or current_page < end_page:
            r.params['params']['page'] = current_page
            r.params['params']['page_size'] = page_size
            if sort:
                r.params['params']['sort'] = sort

            p = await self.exec_req(r)

            ret.extend(p['items'])
            current_page = p['meta']['page']
            page_total = p['meta']['page_total']
            page_size = p['meta']['page_size']

            current_page += 1
            if end_page is None:
                end_page = page_total

        return ret

    class APIRequestFailed(Exception):
        def __init__(self, method, route, params, err_code, err_message):
            self.method = method
            self.route = route
            self.params = params
            self.err_code = err_code
            self.err_message = err_message
