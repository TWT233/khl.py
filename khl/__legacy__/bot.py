"""
deprecated
"""
import shlex
from inspect import Parameter, signature
from typing import Any, List, Union

from ..net_client import BaseClient
from ..cert import Cert
from ..message import TextMsg
from ..command import Command
from ..hardcoded import API_URL
from ..webhook import WebhookClient
from ..websocket import WebsocketClient


class Bot:
    """
    Entity that interacts with user/environment
    """
    def __init__(self,
                 *,
                 cmd_prefix: Union[List[str], str, tuple] = ('!', '！'),
                 cert: Cert,
                 compress: bool = True,
                 **kwargs):
        """
        Constructor of Bot

        :param cmd_prefix: accepted prefix for msg to be a command
        :param cert: used cert for connecting and decrypt
        :param compress: use compressed data to communicate
        """

        self.cmd_prefix = [i for i in cmd_prefix]
        if cert.type == cert.Types.WH:
            args = {'cert': cert, 'compress': compress}

            port = kwargs.get('port')
            if port is not None:
                args['port'] = port

            route = kwargs.get('route')
            if route is not None:
                args['route'] = route
            self.nc: BaseClient = WebhookClient(**args)
        else:
            self.nc: BaseClient = WebsocketClient(cert=cert, compress=compress)

        self.__cmd_list: dict = {}

    def add_command(self, cmd: Command):
        if not isinstance(cmd, Command):
            raise TypeError('not a Command')
        if cmd.name in self.__cmd_list.keys():
            raise ValueError('Command Name Exists')
        self.__cmd_list[cmd.name] = cmd

    def command(self, name: str):
        def decorator(func):
            cmd = Command.command(name)(func)
            self.add_command(cmd)

        return decorator

    async def send(self,
                   channel_id: str,
                   content: str,
                   *,
                   quote: str = '',
                   object_name: int = 1,
                   nonce: str = '') -> Any:
        data = {
            'channel_id': channel_id,
            'content': content,
            'object_name': object_name,
            'quote': quote,
            'nonce': nonce
        }
        return await self.nc.post(f'{API_URL}/channel/message?compress=0',
                                  data)

    def split_msg_args(self, msg: TextMsg):
        if msg.content[0] not in self.cmd_prefix:
            ret = None
        else:
            try:
                ret = shlex.split(msg.content[1:])
            except:
                ret = None
        return ret

    def gen_msg_handler(self):
        async def msg_handler(d: dict):
            msg = TextMsg(self, **d)
            arg_list = self.split_msg_args(msg)
            if arg_list:
                if arg_list[0] in self.__cmd_list.keys():
                    func = self.__cmd_list[arg_list[0]].handler
                    argc = len([
                        1 for v in signature(func).parameters.values()
                        if v.default == Parameter.empty
                    ])
                    if argc <= len(arg_list):
                        await func(
                            msg, *arg_list[1:len(signature(func).parameters)])

        return msg_handler

    def run(self):
        self.nc.on_recv_append(self.gen_msg_handler())
        self.nc.run()
