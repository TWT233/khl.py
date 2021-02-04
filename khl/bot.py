import asyncio
import logging
from typing import Any, Dict, List, Union, Iterable, Callable, Coroutine, TYPE_CHECKING

from aiohttp import ClientSession, ClientResponse

from .command import Command
from .hardcoded import API_URL
from .message import KMDMsg, Msg, SysMsg, TextMsg
from .parser import parser
from .webhook import WebhookClient
from .websocket import WebsocketClient

if TYPE_CHECKING:
    from .cert import Cert
    from .net_client import BaseClient


class Bot:
    """
    Entity that interacts with user/environment
    """
    logger = logging.getLogger('khl.Bot')

    def __init__(self,
                 *,
                 cmd_prefix: Union[List[str], str, tuple] = ('!', '！'),
                 cert: 'Cert',
                 compress: bool = True,
                 **kwargs):
        """
        Constructor of Bot

        :param cmd_prefix: accepted prefix for msg to be a command
        :param net_client: http connector/handler used, usually :class:`khl.webhook.WebhookClient`
        """
        self.cmd_prefix = [i for i in cmd_prefix]
        if cert.type == cert.Types.WEBHOOK:
            args = {'cert': cert, 'compress': compress}

            port = kwargs.get('port')
            if port is not None:
                args['port'] = port

            route = kwargs.get('route')
            if route is not None:
                args['route'] = route
            self.net_client: 'BaseClient' = WebhookClient(**args)
        else:
            self.net_client: 'BaseClient' = WebsocketClient(cert=cert,
                                                            compress=compress)

        self.__cs: ClientSession = ClientSession()
        self.__cmd_index: Dict[str, 'Command'] = {}
        self.__msg_listener: Dict[str, List[Callable[..., Coroutine]]] = {
            'on_raw_event': [],
            'on_all_msg': [],
            'on_text_msg': [],
            'on_system_msg': []
        }

    async def _text_handler(self, msg: TextMsg):
        """
        docstring
        """
        (msg, raw_cmd) = parser(msg, self.cmd_prefix)
        if len(raw_cmd) == 0:
            return None
        inst = self.__cmd_index.get(raw_cmd[0], None)
        if inst:
            self.logger.info(f'cmd triggered: {inst.name} with {raw_cmd}')
            return await inst.execute(msg, *raw_cmd[1:])

    async def _event_handler(self):
        async def _run_event(which: str, msg: Msg):
            for i in self.__msg_listener[which]:
                asyncio.ensure_future(i(msg))

        async def _dispatch_event(msg: Msg):
            await _run_event('on_all_msg', msg)

            if msg.type == Msg.Types.SYS:
                await _run_event('on_system_msg', msg)
            elif msg.type in [Msg.Types.TEXT, Msg.Types.KMD]:
                await _run_event('on_text_msg', msg)
                await self._text_handler(msg)

        while True:
            event = await self.net_client.event_queue.get()
            event['bot'] = self
            self.logger.debug(f'upcoming event:{event}')
            try:
                await _run_event('on_raw_event', event)
                msg = Msg.event_to_msg(event)
                await _dispatch_event(msg)

            except Exception as e:
                self.logger.error(e)
            self.net_client.event_queue.task_done()

    def add_command(self, cmd: 'Command'):
        for i in cmd.trigger:
            if i in self.__cmd_index.keys():
                raise ValueError('Command trigger already exists')
        for i in cmd.trigger:
            self.__cmd_index[i] = cmd
        self.logger.debug(f'cmd added:{cmd.name}')

    def command(self,
                name: str = '',
                aliases: Iterable[str] = (),
                help_doc: str = '',
                desc_doc: str = ''):
        """
        decorator to wrap a func into a Command

        :param name: the name of this Command, also used to trigger
        :param aliases: the aliases, used to trigger Command
        :param help_doc: detailed manual
        :param desc_doc: short introduction
        :return: wrapped Command
        """
        def decorator(func: Callable[..., Coroutine]):
            cmd = Command(func, name, aliases, help_doc, desc_doc)
            self.add_command(cmd)

        return decorator

    def add_msg_listener(self, type: str, func: Callable[..., Coroutine]):
        if type not in self.__msg_listener.keys():
            raise ValueError('event not found')
        self.__msg_listener[type].append(func)

    def on_all_msg(self, func):
        self.add_msg_listener('on_all_msg', func)

    def on_text_msg(self, func):
        self.add_msg_listener('on_text_msg', func)

    def on_system_msg(self, func):
        self.add_msg_listener('on_system_msg', func)

    def on_raw_event(self, func):
        self.add_msg_listener('on_raw_event', func)

    async def get(self, url, **kwargs) -> ClientResponse:
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bot {self.net_client.cert.token}'

        async with self.__cs.post(url, headers=headers, **kwargs) as res:
            await res.read()
            return res

    async def post(self, url, **kwargs) -> ClientResponse:
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bot {self.net_client.cert.token}'
        headers['Content-type'] = 'application/json'

        async with self.__cs.post(url, headers=headers, **kwargs) as res:
            await res.read()
            return res

    async def send(self,
                   channel_id: str,
                   content: str,
                   *,
                   quote: str = '',
                   type: int = Msg.Types.KMD,
                   nonce: str = '',
                   temp_target_id: str = '') -> ClientResponse:
        data = {
            'channel_id': channel_id,
            'content': content,
            'type': type,
            'quote': quote,
            'nonce': nonce,
            'temp_target_id': temp_target_id
        }
        return await self.post(f'{API_URL}/channel/message?compress=0',
                               json=data)

    async def user_grant_role(self, user_id: str, guild_id: str,
                              role_id: str) -> Any:
        return await self.post(f'{API_URL}/guild-role/grant?compress=0',
                               json={
                                   'user_id': user_id,
                                   'guild_id': guild_id,
                                   'role_id': role_id
                               })

    async def user_revoke_role(self, user_id: str, guild_id: str,
                               role_id: str) -> Any:
        return await self.post(f'{API_URL}/guild-role/revoke?compress=0',
                               json={
                                   'user_id': user_id,
                                   'guild_id': guild_id,
                                   'role_id': role_id
                               })

    def run(self):
        self.logger.info('launching')
        asyncio.ensure_future(self.net_client.run())
        asyncio.ensure_future(self._event_handler())
        asyncio.get_event_loop().run_forever()
