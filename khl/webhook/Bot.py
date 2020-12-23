import asyncio
import json
import shlex
import zlib
from inspect import signature, Parameter
from typing import Union

from aiohttp import web, ClientSession

from .cert import Cert
from ..utils import API_URL, TextMsg, Command


class Bot:
    def __init__(self, *,
                 port: int = 5000, compress: bool = True,
                 cmd_prefix: Union[list, str, tuple] = ('!', '！'),
                 cert: Cert):
        self.port: int = port
        self.compress = compress
        self.cmd_prefix = [i for i in cmd_prefix]
        self.cert = cert

        self.app = web.Application()
        self.__cmd_list: dict = {}

    def command(self, name: str):
        def cmd_wrapper(func):
            if name in self.__cmd_list.keys():
                raise TypeError
            self.__cmd_list[name] = func
            return func

        return cmd_wrapper

    def check_msg_is_cmd(self, msg: TextMsg):
        return (msg.content[0] not in self.cmd_prefix) and None or shlex.split(msg.content[1:])

    def data_to_json(self, data: bytes):
        data = self.compress and zlib.decompress(data) or data
        data = json.loads(str(data, encoding='utf-8'))
        return ('encrypt' in data.keys()) and json.loads(self.cert.decrypt(data['encrypt'])) or data

    async def send(self, channel_id: str, content: str, *, quote: str = '', object_name: int = 1, nonce: str = ''):
        headers = {'Authorization': f'Bot {self.cert.token}', 'Content-type': 'application/json'}
        data = {'channel_id': channel_id, 'content': content, 'object_name': object_name, 'quote': quote,
                'nonce': nonce}
        return await ClientSession().post(f'{API_URL}/channel/message?compress=0', headers=headers, json=data)

    def run(self):
        async def respond(request: web.Request) -> web.Response:
            json_data = self.data_to_json(await request.read())
            assert json_data
            assert json_data['d']['verify_token'] == self.cert.verify_token

            if json_data['s'] == 0:
                d = json_data['d']
                if d['type'] == 1:
                    msg = TextMsg(channel_type=d['channel_type'], target_id=d['target_id'],
                                  author_id=d['author_id'], content=d['content'], msg_id=d['msg_id'],
                                  msg_timestamp=d['msg_timestamp'], nonce=d['nonce'], extra=d['extra'])
                    arg_list = self.check_msg_is_cmd(msg)
                    if arg_list:
                        if arg_list[0] in self.__cmd_list.keys():
                            func = self.__cmd_list[arg_list[0]]
                            argc = len([1 for v in signature(func).parameters.values() if v.default == Parameter.empty])
                            if argc <= len(arg_list):
                                func(msg, *arg_list[1:len(signature(func).parameters)])
                if d['type'] == 255:
                    if d['channel_type'] == 'WEBHOOK_CHALLENGE':
                        return web.json_response({'challenge': d['challenge']})

            return web.Response(status=200)

        self.app.router.add_post('/khl-wh', respond)
        web.run_app(self.app, port=self.port)
