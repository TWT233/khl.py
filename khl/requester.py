import asyncio
import functools
import inspect
import logging
import re
from typing import Union, Dict, Callable

from aiohttp import ClientSession

from .cert import Cert
from .interface import AsyncRunnable

log = logging.getLogger(__name__)

API = f'https://www.kaiheila.cn/api/v3'


class _Req:
    def __init__(self, method: str, route: str, params: Dict):
        self.method = method
        self.route = route
        self.params = params


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
            log.debug(f'req: [{route}]({params})')
            rsp = await res.json()
            if rsp['code'] != 0:
                log.error(f'req failed: {rsp}, req:[{route}]({params})')
            else:
                log.debug(f'req done: {rsp}')
            return rsp['data']

    async def exec_req(self, r: _Req):
        return await self.request(r.method, r.route, **r.params)


def req(method: str):
    def _method(func: Callable):
        @functools.wraps(func)
        def req_maker(*args, **kwargs) -> _Req:
            param_names = list(inspect.signature(func).parameters.keys())
            for i in range(len(args)):
                kwargs[param_names[i]] = args[i]
            route = re.sub(r'(?<!^)(?=[A-Z])', '-', func.__qualname__).lower().replace('.', '/')
            return _Req(method, route, kwargs)

        return req_maker

    return _method


class Channel:
    @staticmethod
    @req('GET')
    def list(
            guild_id
    ):
        ...

    @staticmethod
    @req('GET')
    def view(
            target_id
    ):
        ...

    @staticmethod
    @req('POST')
    def create(
            guild_id,
            parent_id,
            name,
            type,
            limit_amount,
            voice_quality,
    ):
        ...

    @staticmethod
    @req('POST')
    def delete(
            channel_id
    ):
        ...

    @staticmethod
    @req('POST')
    def moveUser(
            target_id,
            user_ids
    ):
        ...


class ChannelRole:

    @staticmethod
    @req('GET')
    def index(
            channel_id
    ):
        ...

    @staticmethod
    @req('POST')
    def create(
            channel_id,
            type,
            value,
    ):
        ...

    @staticmethod
    @req('POST')
    def update(
            channel_id,
            type,
            value,
            allow,
            deny,
    ):
        ...

    @staticmethod
    @req('POST')
    def delete(
            channel_id,
            type,
            value,
    ):
        ...
