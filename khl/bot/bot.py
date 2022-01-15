import asyncio
import logging
from typing import Dict, Callable, List, Optional, Union

from .. import AsyncRunnable, MessageTypes, EventTypes  # interfaces & basics
from .. import Cert, HTTPRequester, WebhookReceiver, WebsocketReceiver, Gateway, Client  # net related
from .. import User, Channel, PublicChannel, PublicTextChannel, Guild, Event, Message  # concepts
from ..command import CommandManager
from ..task import TaskManager

log = logging.getLogger(__name__)


class Bot(AsyncRunnable):
    """
    Represents a entity that handles msg/events and interact with users/khl server in manners that programmed.
    """
    # components
    client: Client
    command: CommandManager
    task: TaskManager

    # flags
    _is_running: bool

    # internal containers
    _me: Optional[User]
    _event_index: Dict[EventTypes, List[Callable]]

    def __init__(self, token: str = '', *, cert: Cert = None, client: Client = None, gate: Gateway = None,
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
        self._init_client(cert or Cert(token=token), client, gate, out, compress, port, route)
        self.client.register(MessageTypes.TEXT, self._make_msg_handler())
        self.client.register(MessageTypes.SYS, self._make_event_handler())

        self.command = CommandManager()
        self.task = TaskManager()

        self._is_running = False

        self._me = None
        self._event_index = {}
        self._tasks = []

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

        async def handler(msg: Message):
            await self.command.handle(self.loop, msg, {Message: msg, Bot: self})

        return handler

    def _make_event_handler(self) -> Callable:
        async def handler(event: Event):
            if event.event_type not in self._event_index:
                return
            if not self._event_index[event.event_type]:
                return
            for h in self._event_index[event.event_type]:
                await h(self, event)

        return handler

    def add_event_handler(self, type: EventTypes, handler: Callable):
        if type not in self._event_index:
            self._event_index[type] = []
        self._event_index[type].append(handler)
        log.debug(f'event_handler {handler.__qualname__} for {type} added')
        return handler

    def on_event(self, type: EventTypes):
        """
        decorator, register a function to handle events of the type

        :param type: the type
        :return: original func
        """
        return lambda func: self.add_event_handler(type, func)

    async def fetch_me(self, force_update: bool = False) -> User:
        """fetch detail of the bot it self as a ``User``"""
        if not self._me or not self._me.is_loaded():
            self._me = await self.client.fetch_me(force_update)
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

    async def fetch_public_channel(self, channel_id: str) -> PublicChannel:
        """fetch details of a public channel from khl"""
        return await self.client.fetch_public_channel(channel_id)

    async def fetch_guild(self, guild_id: str) -> Guild:
        """fetch details of a guild from khl"""
        guild = Guild(_gate_=self.client.gate, id=guild_id)
        await guild.load()
        return guild

    async def list_guild(self) -> List[Guild]:
        """list guilds the bot joined"""
        return await self.client.list_guild()

    @staticmethod
    async def send(target: Channel, content: Union[str, List], *, temp_target_id: str = '', **kwargs):
        """
        send a msg to a channel

        ``temp_target_id`` is only available in ChannelPrivacyTypes.GROUP
        """
        if isinstance(target, PublicTextChannel):
            kwargs['temp_target_id'] = temp_target_id

        return await target.send(content, **kwargs)

    async def upload_asset(self, file: str) -> str:
        """upload ``file`` to khl, and return the url to the file, alias for ``create_asset``"""
        return await self.client.create_asset(file)

    async def create_asset(self, file: str) -> str:
        """upload ``file`` to khl, and return the url to the file"""
        return await self.client.create_asset(file)

    async def kickout(self, guild: Guild, user: Union[User, str]):
        """kick ``user`` out from ``guild``"""
        if guild.gate.requester != self.client.gate.requester:
            raise ValueError('can not modify guild from other gate')
        return await guild.kickout(user)

    async def leave(self, guild: Guild):
        """leave from ``guild``"""
        if guild.gate.requester != self.client.gate.requester:
            raise ValueError('can not modify guild from other gate')
        return await guild.leave()

    async def _make_temp_msg(self, msg_id: str) -> Message:
        return Message(msg_id=msg_id, _gate_=self.client.gate)

    async def delete_message(self, msg: Union[Message, str]):
        """delete msg

        wraps `Message.delete`

        :param msg: the msg, accepts Message and msg_id(str)
        """
        if isinstance(msg, str):
            msg = self._make_temp_msg(msg)
        return await msg.delete()

    async def add_reaction(self, msg: Union[Message, str], emoji: str):
        """add emoji to msg's reaction list

        wraps `Message.add_reaction`

        :param msg: accepts `Message` and msg_id(str)
        :param emoji: 😘
        """
        if isinstance(msg, str):
            msg = self._make_temp_msg(msg)
        return await msg.add_reaction(emoji)

    async def delete_reaction(self, msg: Union[Message, str], emoji: str, user: User = None):
        """delete emoji from msg's reaction list

        wraps `Message.delete_reaction`

        :param msg: accepts `Message` and msg_id(str)
        :param emoji: 😘
        :param user: whose reaction, delete others added reaction requires channel msg admin permission
        """
        if isinstance(msg, str):
            msg = self._make_temp_msg(msg)
        return await msg.delete_reaction(emoji, user)

    async def start(self):
        if self._is_running:
            raise RuntimeError('this bot is already running')
        self.task.schedule()
        await self.client.start()

    def run(self):
        if not self.loop:
            self.loop = asyncio.get_event_loop()
        try:
            self.loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            log.info('see you next time')
