import asyncio
import json
import logging
from typing import Any, Dict, List, Union, Iterable, Callable, Coroutine, TYPE_CHECKING

from aiohttp import ClientSession, FormData

from .command import Command
from .hardcoded import API_URL
from .kqueue import KQueue
from .message import Msg, SysMsg, TextMsg, BtnTextMsg
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
    use_btn_command = True

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
        self.kq: Dict[str, KQueue] = {'btn': KQueue(), 'user': KQueue()}
        self.__me: Dict = {}
        self.__msg_listener: Dict[str, List[Callable[..., Coroutine]]] = {
            'on_raw_event': [],
            'on_all_msg': [],
            'on_text_msg': [],
            'on_system_msg': []
        }

    async def id(self):
        if not self.__me or 'id' not in self.__me.keys():
            self.__me = await self.get(f'{API_URL}/user/me')
        return self.__me['id']

    async def _btn_watcher(self, msg: SysMsg):
        if msg.event_type != SysMsg.EventTypes.BTN_CLICK or self.use_btn_command is False:
            return

        try:
            b = msg.extra['body']
            cmd = ''
            for i in self.cmd_prefix:
                if b['value'].startswith(i):
                    cmd = b['value']
                    break
            if not cmd:
                cmd = self.cmd_prefix[0] + json.loads(b['value'])['cmd']

            msg.ret_val = cmd
            await self._cmd_handler(BtnTextMsg(msg))
        except json.JSONDecodeError:
            await self.kq['btn'].put(msg.extra['body']['msg_id'], msg)

    async def _cmd_handler(self, msg: TextMsg):
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
        else:
            return None

    async def _event_handler(self):
        async def _run_event(which: str, msg: Msg):
            for i in self.__msg_listener[which]:
                asyncio.ensure_future(i(msg))

        async def _dispatch_event(e: dict):
            event_with_bot = {**event, 'bot': self}
            for i in self.__msg_listener['on_raw_event']:
                asyncio.ensure_future(i(event_with_bot))

            m = Msg.event_to_msg(event_with_bot)
            if not m:
                self.logger.warning(f'unrecognized event:\n\t{e}')
                return

            await _run_event('on_all_msg', m)

            if m.type == Msg.Types.SYS:
                m: SysMsg
                await _run_event('on_system_msg', m)
                await self._btn_watcher(m)
            elif m.type in [Msg.Types.TEXT, Msg.Types.KMD, Msg.Types.CARD]:
                m: TextMsg
                await _run_event('on_text_msg', m)
                await self.kq['user'].put(m.author_id, m)
                await self._cmd_handler(m)

        while True:
            event = await self.net_client.event_queue.get()
            self.logger.debug(f'upcoming event:\n\t{event}')

            asyncio.ensure_future(_dispatch_event(event))

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

    async def get(self, url, **kwargs) -> Union[dict, list]:
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bot {self.net_client.cert.token}'

        async with self.__cs.get(url, headers=headers, **kwargs) as res:
            rsp = await res.json()
            log_str = f'{url}\n\tparams: {kwargs}\n\tresult: {rsp}'
            if rsp['code'] != 0:
                self.logger.error(f'request failed: {log_str}')
            else:
                self.logger.debug(f'req done: {log_str}')
            return rsp['data']

    async def post(self, url, **kwargs) -> Union[dict, list]:
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bot {self.net_client.cert.token}'

        async with self.__cs.post(url, headers=headers, **kwargs) as res:
            rsp = await res.json()
            log_str = f'{url}\n\tparams: {kwargs}\n\tresult: {rsp}'
            if rsp['code'] != 0:
                self.logger.error(f'request failed: {log_str}')
            else:
                self.logger.debug(f'req done: {log_str}')
            return rsp['data']

    async def upload_asset(self, file: str):
        return await self.post(f'{API_URL}/asset/create',
                               data={'file': open(file, 'rb')})

    async def send(self,
                   channel_id: str,
                   content: str,
                   *,
                   quote: str = '',
                   type: int = Msg.Types.KMD,
                   nonce: str = '',
                   temp_target_id: str = '') -> Union[dict, list]:
        data = {
            'channel_id': channel_id,
            'content': content,
            'type': type,
            'quote': quote,
            'nonce': nonce,
            'temp_target_id': temp_target_id
        }
        return await self.post(f'{API_URL}/message/create', json=data)

    async def delete(self, msg_id: str) -> Union[dict, list]:
        data = {'msg_id': msg_id}
        return await self.post(f'{API_URL}/message/delete', json=data)

    async def update(self, msg_id, content, *, quote='') -> Union[dict, list]:
        data = {'msg_id': msg_id, 'content': content, 'quote': quote}
        return await self.post(f'{API_URL}/message/update?compress=0',
                               json=data)

    async def send_dm(self,
                      target_id: str,
                      content: str,
                      *,
                      quote: str = '',
                      type: int = Msg.Types.KMD,
                      nonce: str = ''):
        data = {
            'target_id': target_id,
            'content': content,
            'type': type,
            'quote': quote,
            'nonce': nonce
        }
        return await self.post(f'{API_URL}/direct-message/create', json=data)

    async def update_dm(self, msg_id: str, content: str, quote: str = ''):
        data = {'msg_id': msg_id, 'content': content, 'quote': quote}
        return await self.post(f'{API_URL}/direct-message/update', json=data)

    async def delete_dm(self, msg_id: str):
        data = {'msg_id': msg_id}
        return await self.post(f'{API_URL}/direct-message/delete', json=data)

    async def user_grant_role(self, user_id: str, guild_id: str,
                              role_id: int) -> Any:
        data = {'user_id': user_id, 'guild_id': guild_id, 'role_id': role_id}
        return await self.post(f'{API_URL}/guild-role/grant', json=data)

    async def user_revoke_role(self, user_id: str, guild_id: str,
                               role_id: int) -> Any:
        data = {'user_id': user_id, 'guild_id': guild_id, 'role_id': role_id}
        return await self.post(f'{API_URL}/guild-role/revoke', json=data)

    def run(self):
        try:
            self.logger.info('launching')
            asyncio.ensure_future(self._event_handler())
            asyncio.get_event_loop().run_until_complete(self.net_client.run())
        except KeyboardInterrupt:
            pass
        asyncio.get_event_loop().run_until_complete(self.__cs.close())
        self.logger.info('see you next time')
