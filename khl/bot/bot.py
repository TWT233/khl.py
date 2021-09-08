import asyncio
import logging
from typing import Dict, Callable, List, Optional, Union, Pattern

import api
from khl import Channel, PublicTextChannel
from .command import Command
from .lexer import Lexer
from .parser import Parser
from .. import (AsyncRunnable, User, Message, MessageTypes,
                Cert, HTTPRequester, WebhookReceiver, WebsocketReceiver, Gateway, Client, )

log = logging.getLogger(__name__)


class Bot(AsyncRunnable):
    """
    Represents a entity that handles msg/events and interact with users/khl server in manners that programmed.
    """
    client: Client
    _me: Optional[User]
    _cmd_index: Dict[str, Command] = {}

    def __init__(self, *, token: str = '', cert: Cert = None, client: Client = None, gate: Gateway = None,
                 out: HTTPRequester = None, compress: bool = True, port=5000, route='/khl-wh'):
        """
        The most common usage: ``Bot(token='xxxxxx')``

        That's enough.

        :param cert: used to build requester and receiver
        :param client: the bot relies on
        :param gate: the client relies on
        :param out: the gate's component
        :param compress: used to tune the receiver
        :param port: used to tune the WebhookReceiver
        :param route: used to tune the WebhookReceiver
        """
        if not token and not cert:
            raise ValueError('require token or cert')
        self._init_client(cert if cert else Cert(token=token), client, gate, out, compress, port, route)
        self._me = None
        self.client.register(MessageTypes.TEXT, self._make_msg_handler())

    def _init_client(self, cert: Cert, client: Client, gate: Gateway, out: HTTPRequester, compress: bool, port, route):
        """
        construct self.client from args.

        you can init client with kinds of filling ways,
        so there is a priority in the rule: client > gate > out = compress = port = route

        :param cert: used to build requester and receiver
        :param client: the bot relies on
        :param gate: the client relies on
        :param out: the gate's component
        :param compress: used to tune the receiver
        :param port: used to tune the WebhookReceiver
        :param route: used to tune the WebhookReceiver
        :return:
        """
        if client:
            self.client = client
            return
        if gate:
            self.client = Client(gate)
            return

        # client and gate not in args, build them
        _out = out if out else HTTPRequester(cert)
        if cert.type == Cert.Types.WEBSOCKET:
            _in = WebsocketReceiver(cert, compress)
        elif cert.type == Cert.Types.WEBHOOK:
            _in = WebhookReceiver(cert, port=port, route=route, compress=compress)
        else:
            raise ValueError(f'cert type: {cert.type} not supported')

        self.client = Client(Gateway(_out, _in))

    def _make_msg_handler(self) -> Callable:
        """
        construct a function to receive msg from client, and interpret it with _cmd_index
        """

        # use closure
        async def handler(msg: Message):
            for name, cmd in self._cmd_index.items():
                try:
                    args = cmd.prepare(msg)
                except Lexer.LexerException:  # TODO: a more reasonable exception handle in lex and parse
                    continue
                await cmd.execute(msg, *args)

        return handler

    def add_command(self, cmd: Command) -> Command:
        """
        register the cmd on current Bot

        :param cmd: the Command going to be registered
        :return: the cmd
        """
        if cmd.name in self._cmd_index:
            raise ValueError(f'cmd: {cmd.name} already exists')
        self._cmd_index[cmd.name] = cmd
        log.debug(f'cmd: {cmd.name} added')
        return cmd

    def command(self, name: str = '', *, help: str = '', desc: str = '',
                aliases: List[str] = (), prefixes: List[str] = ('/',), regex: Union[str, Pattern] = '',
                lexer: Lexer = None, parser: Parser = None):
        """
        decorator, wrap a function in Command and register it on current Bot

        :param name: the name of this Command, also used to trigger in DefaultLexer
        :param aliases: you can also trigger the command with aliases (DefaultLexer only)
        :param prefixes: command prefix, default use '/' (DefaultLexer only)
        :param regex:
        :param help: detailed manual
        :param desc: short introduction
        :param lexer: the lexer used (Advanced)
        :param parser: the parser used (Advanced)
        :return: wrapped Command
        """
        args = {'help': help, 'desc': desc,
                'aliases': aliases, 'prefixes': prefixes, 'regex': regex,
                'lexer': lexer, 'parser': parser}
        return lambda func: self.add_command(Command.command(name, **args)(func))

    async def fetch_me(self, force_update: bool = False) -> User:
        if force_update or not self._me or not self._me.is_loaded():
            self._me = User(**(await self.client.gate.exec_req(api.User.me())), _lazy_loaded_=True)
        return self._me

    @property
    def me(self) -> User:
        """
        get bot it self's data

        RECOMMEND: use ``await fetch_me()``

        CAUTION: please call ``await fetch_me()`` first to load data from khl server

        designed as 'empty-then-fetch' will break the rule 'net-related is async'

        :return: the bot's underlying User
        """
        if self._me and self._me.is_loaded():
            return self._me
        raise ValueError('not loaded, please call `await fetch_me()` first')

    @staticmethod
    async def send(target: Channel, content: Union[str, List], *, temp_target_id: str = '', **kwargs):
        """
        send a msg to a channel

        ``temp_target_id`` is only available in ChannelPrivacyTypes.GROUP
        """
        if isinstance(target, PublicTextChannel):
            kwargs['temp_target_id'] = temp_target_id

        return await target.send(content, **kwargs)

    def run(self):
        try:
            if not self.loop:
                self.loop = asyncio.get_event_loop()
            self.loop.run_until_complete(self.client.run())
        except KeyboardInterrupt:
            pass
        except Exception as e:
            log.error(e)
        log.info('see you next time')
