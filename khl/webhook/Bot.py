import json
import logging
import shlex
import zlib
from inspect import signature, Parameter
from typing import Union

import requests
from flask import Flask, request, Response

from ..utils import API_URL, TextMsg
from .cert import Cert


class Bot:
    def __init__(self, *,
                 port: int = 5000, compress: bool = True,
                 cmd_prefix: Union[list, str, tuple] = ('!', '！'),
                 cert: Cert):
        self.port: int = port
        self.compress = compress
        self.cmd_prefix = [i for i in cmd_prefix]
        self.cert = cert

        self.app = Flask(__name__)
        self.__cmd_list: dict = {}

    def command(self, name: str):
        # TODO: check func args
        def cmd_wrapper(func):
            if name in self.__cmd_list.keys():
                raise TypeError
            self.__cmd_list[name] = func
            return func

        return cmd_wrapper

    def check_msg_is_cmd(self, msg: TextMsg):
        if msg.content[0] not in self.cmd_prefix:
            return None
        return shlex.split(msg.content[1:])

    def data_to_json(self, data: bytes):
        data = self.compress and zlib.decompress(data) or data
        data = json.loads(str(data, encoding='utf-8'))
        if 'encrypt' in data.keys():
            data = json.loads(self.cert.decrypt(data['encrypt']))
        return data

    def send(self, channel_id: str, content: str, *, quote: str = '', object_name: int = 1, nonce: str = ''):
        headers = {'Authorization': f'Bot {self.cert.token}', 'Content-type': 'application/json'}
        data = {'channel_id': channel_id, 'content': content, 'object_name': object_name}
        if quote:
            data['quote'] = quote
        if nonce:
            data['nonce'] = nonce

        return requests.post(f'{API_URL}/channel/message?compress=0', headers=headers, data=json.dumps(data))

    def run(self):
        @self.app.route('/khl-wh', methods=['POST'])
        def respond():
            json_data = self.data_to_json(request.data)
            logging.debug(json_data)
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

                    return Response(status=200)
                if d['type'] == 255:
                    if d['channel_type'] == 'WEBHOOK_CHALLENGE':
                        return {'challenge': d['challenge']}

            return Response(status=200)

        self.app.run(host="0.0.0.0", port=self.port)
