import asyncio
import logging
from typing import Union, List, Optional

from aiohttp import ClientSession

from .ratelimiter import RateLimiter
from .api import _Req
from .cert import Cert

log = logging.getLogger(__name__)

API = 'https://www.kookapp.cn/api/v3'


class HTTPRequester:
    """wrap raw requests, handle boilerplate param filling works"""

    def __init__(self, cert: Cert, ratelimiter: Optional[RateLimiter]):
        self._cert = cert
        self._cs: Union[ClientSession, None] = None
        self._ratelimiter = ratelimiter

    def __del__(self):
        if self._cs is not None:
            asyncio.get_event_loop().run_until_complete(self._cs.close())

    async def request(self, method: str, route: str, **params) -> Union[dict, list, bytes]:
        """wrap raw request, fill authorization, handle & extract response"""
        headers = params.pop('headers', {})
        params['headers'] = headers

        log.debug(f'{method} {route}: req: {params}')  # token is excluded

        if self._ratelimiter is not None:
            await self._ratelimiter.wait_for_rate(route)

        headers['Authorization'] = f'Bot {self._cert.token}'
        if self._cs is None:  # lazy init
            self._cs = ClientSession()
        async with self._cs.request(method, f'{API}/{route}', **params) as res:
            if res.content_type == 'application/json':
                rsp = await res.json()
                if rsp['code'] != 0:
                    raise HTTPRequester.APIRequestFailed(method, route, params, rsp['code'], rsp['message'])
                rsp = rsp['data']
            else:
                rsp = await res.read()

            if self._ratelimiter is not None:
                await self._ratelimiter.update(route, res.headers)

            log.debug(f'{method} {route}: rsp: {rsp}')
            return rsp

    async def exec_req(self, r: _Req):
        """_Req -> raw request"""
        return await self.request(r.method, r.route, **r.params)

    async def exec_paged_req(self,
                             r: _Req,
                             *,
                             begin_page: int = 1,
                             end_page: int = None,
                             page_size: int = 50,
                             sort: str = '') -> List:
        """
        execute paged requests

        iter from ``begin_page`` to the ``end_page``, ``end_page=None`` means to the end

        1. get a req, inject the params
        2. req and receive the result
        3. unwrap the result, append result, fresh pagination params

        :param begin_page: int = 1,
        :param end_page: int = None,
        :param page_size: int = 50,
        :param sort: str = ''
        """
        ret = []
        current_page = begin_page
        while end_page is None or current_page <= end_page:
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
        """Raised when khl.py received non-zero error code from remote server.

        By default, params (request body) is not included when calling __str__ on it, to avoid leaking credential
        into logs;

        if request body is needed for debug purpose, consider explicitly catching this exception and
        call repr(...) with the exception instance."""

        def __init__(self, method, route, params, err_code, err_message):
            super().__init__()
            self.method = method
            self.route = route
            self.params = params
            self.err_code = err_code
            self.err_message = err_message

        def __str__(self):
            return f"Requesting '{self.method} {self.route}' failed with {self.err_code}: {self.err_message}"
