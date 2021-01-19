import shlex
from typing import Any, Dict, List, Union

from khl import BaseClient, Cert, TextMsg
from khl.command_preview import parser
from khl.command_preview.typings import BaseCommand

from .hardcoded import API_URL
from .webhook import WebhookClient
from .websocket import WebsocketClient


class BotPreview:
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
        :param net_client: http connector/handler used, usually :class:`khl.webhook.WebhookClient`
        """
        self.cmd_prefix = [i for i in cmd_prefix]
        if cert.type == 'webhook':
            args = {'cert': cert, 'compress': compress}

            port = kwargs.get('port')
            args['port'] = port if port else 8600

            route = kwargs.get('route')
            if route is not None:
                args['route'] = route
            self.nc: BaseClient = WebhookClient(**args)
        else:
            self.nc: BaseClient = WebsocketClient(cert=cert, compress=compress)
        self.__cmd_list_preview: Dict[str, BaseCommand] = {}

    def add_command(self, cmd: BaseCommand):
        # if not isinstance(cmd, BaseCommand):
        #     raise TypeError('not a Command')
        if cmd.name in self.__cmd_list_preview.keys():
            raise ValueError('Command Name Exists')
        self.__cmd_list_preview[cmd.name] = cmd

    def gen_msg_handler_preview(self):
        async def msg_handler_preview(d: Dict[Any, Any]):
            """
            docstring
            """
            print(d)
            res = parser(d, self.cmd_prefix, self.__cmd_list_preview)
            if isinstance(res, TextMsg):
                return None
            (command_str, args, msg) = res
            result = self.__cmd_list_preview[command_str].execute(
                command_str, args, msg)
            return await result

        return msg_handler_preview

    # def command(self, name: str):
    #     def decorator(func):
    #         cmd = Command.command(name)(func)
    #         self.add_command(cmd)

    #     return decorator

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
        return await self.nc.send(f'{API_URL}/channel/message?compress=0',
                                  data)


    # def gen_msg_handler(self):
    #     async def msg_handler(d: dict):
    #         msg = TextMsg(channel_type=d['channel_type'],
    #                       target_id=d['target_id'],
    #                       author_id=d['author_id'],
    #                       content=d['content'],
    #                       msg_id=d['msg_id'],
    #                       msg_timestamp=d['msg_timestamp'],
    #                       nonce=d['nonce'],
    #                       extra=d['extra'])
    #         arg_list = self.split_msg_args(msg)
    #         if arg_list:
    #             if arg_list[0] in self.__cmd_list.keys():
    #                 func = self.__cmd_list[arg_list[0]].handler
    #                 argc = len([
    #                     1 for v in signature(func).parameters.values()
    #                     if v.default == Parameter.empty
    #                 ])
    #                 if argc <= len(arg_list):
    #                     await func(
    #                         msg, *arg_list[1:len(signature(func).parameters)])

    #     return msg_handler

    def run(self):
        self.nc.on_recv_append(self.gen_msg_handler_preview())
        self.nc.run()
