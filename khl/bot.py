import asyncio
import logging
from typing import Any, Dict, List, Union, Iterable, Callable, Coroutine, TYPE_CHECKING

from .command import Command
from .hardcoded import API_URL
from .message import Msg
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

        self.__cmd_index: Dict[str, 'Command'] = {}
        self.__event_list: Dict[str, List[Callable[..., Coroutine]]] = {
            'on_all_events': [],
            'on_message': [],
            'on_system_event': []
        }

    async def _text_handler(self, event: Dict[Any, Any]):
        """
        docstring
        """
        logging.debug(event)
        event['bot'] = self
        (msg, raw_cmd) = parser(event, self.cmd_prefix)
        if len(raw_cmd) == 0:
            return None
        inst = self.__cmd_index.get(raw_cmd[0], None)
        if inst:
            return await inst.execute(msg, *raw_cmd[1:])

    async def _event_handler(self):
        async def _run_event(which: str):
            for i in self.__event_list[which]:
                asyncio.ensure_future(i(event))

        while True:
            event = await self.net_client.event_queue.get()
            try:
                await _run_event('on_all_events')

                if event['type'] == Msg.Types.SYS:
                    await _run_event('on_system_event')
                else:
                    await _run_event('on_message')
                    if event['type'] == Msg.Types.TEXT:
                        await self._text_handler(event)

            except Exception as e:
                logging.warning(e)
                pass
            self.net_client.event_queue.task_done()

    def add_command(self, cmd: 'Command'):
        for i in cmd.trigger:
            if i in self.__cmd_index.keys():
                raise ValueError('Command trigger already exists')
        for i in cmd.trigger:
            self.__cmd_index[i] = cmd

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

    def add_event_listener(self, type: str, func: Callable[..., Coroutine]):
        if type not in self.__event_list.keys():
            raise ValueError('event not found')
        self.__event_list[type].append(func)

    def on_all_events(self, func):
        self.add_event_listener('on_all_events', func)

    def on_message(self, func):
        self.add_event_listener('on_message', func)

    def on_system_event(self, func):
        self.add_event_listener('on_system_event', func)

    async def send(self,
                   channel_id: str,
                   content: str,
                   *,
                   quote: str = '',
                   type: int = Msg.Types.KMD,
                   nonce: str = '') -> Any:
        data = {
            'channel_id': channel_id,
            'content': content,
            'type': type,
            'quote': quote,
            'nonce': nonce
        }
        return await self.net_client.post(
            f'{API_URL}/channel/message?compress=0', data)

    async def user_grant_role(self, user_id: str, guild_id: str,
                              role_id: str) -> Any:
        return await self.net_client.post(
            f'{API_URL}/guild-role/grant?compress=0', {
                'user_id': user_id,
                'guild_id': guild_id,
                'role_id': role_id
            })

    async def user_revoke_role(self, user_id: str, guild_id: str,
                               role_id: str) -> Any:
        return await self.net_client.post(
            f'{API_URL}/guild-role/revoke?compress=0', {
                'user_id': user_id,
                'guild_id': guild_id,
                'role_id': role_id
            })

    def run(self):
        asyncio.ensure_future(self.net_client.run())
        asyncio.ensure_future(self._event_handler())
        asyncio.get_event_loop().run_forever()
