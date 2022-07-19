import asyncio
import logging
from typing import Dict, Callable, List, Optional, Union, Coroutine, IO

from .. import AsyncRunnable, MessageTypes, EventTypes  # interfaces & basics
from .. import Cert, HTTPRequester, WebhookReceiver, WebsocketReceiver, Gateway, Client  # net related
from .. import User, Channel, PublicChannel, PublicTextChannel, Guild, Event, Message  # concepts
from ..command import CommandManager
from ..game import Game
from ..interface import SlowModeTypes, SoftwareTypes
from ..task import TaskManager

log = logging.getLogger(__name__)

TypeEventHandler = Callable[['Bot', Event], Coroutine]
MessageHandler = Callable[[Message], Coroutine]


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
    _event_index: Dict[EventTypes, List[TypeEventHandler]]

    def __init__(self,
                 token: str = '',
                 *,
                 cert: Cert = None,
                 client: Client = None,
                 gate: Gateway = None,
                 out: HTTPRequester = None,
                 compress: bool = True,
                 port=5000,
                 route='/khl-wh'):
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
        msg_handler = self._make_msg_handler()
        self.client.register(MessageTypes.TEXT, msg_handler)
        self.client.register(MessageTypes.KMD, msg_handler)
        self.client.register(MessageTypes.SYS, self._make_event_handler())
        self.command = CommandManager()
        self.task = TaskManager()

        self._is_running = False

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

    def add_event_handler(self, type: EventTypes, handler: TypeEventHandler):
        if type not in self._event_index:
            self._event_index[type] = []
        self._event_index[type].append(handler)
        log.debug(f'event_handler {handler.__qualname__} for {type} added')
        return handler

    def add_message_handler(self, handler: MessageHandler, *except_type: MessageTypes):
        """`except_type` is an exclusion list"""
        for type in MessageTypes:
            if type not in except_type:
                self.client.register(type, handler)

    def on_event(self, type: EventTypes):
        """
        decorator, register a function to handle events of the type

        :param type: the type
        """

        def dec(func: TypeEventHandler):
            self.add_event_handler(type, func)

        return dec

    def on_message(self, *except_type: MessageTypes):
        """
        decorator, register a function to handle messages
        :param except_type: excepted types
        """

        def dec(func: MessageHandler):
            self.add_message_handler(func, *set(except_type + (MessageTypes.SYS,)))

        return dec

    async def fetch_me(self, force_update: bool = False) -> User:
        """fetch detail of the bot it self as a ``User``"""
        return await self.client.fetch_me(force_update)

    @property
    def me(self) -> User:
        """
        get bot it self's data

        RECOMMEND: use ``await fetch_me()``

        CAUTION: please call ``await fetch_me()`` first to load data from khl server

        designed as 'empty-then-fetch' will break the rule 'net-related is async'

        :return: the bot's underlying User
        """
        return self.client.me

    async def fetch_public_channel(self, channel_id: str) -> PublicChannel:
        """fetch details of a public channel from khl"""
        return await self.client.fetch_public_channel(channel_id)

    async def fetch_user(self, user_id: str) -> User:
        return await self.client.fetch_user(user_id)

    async def delete_channel(self, channel: Union[Channel, str]):
        """delete a channel, permission required"""
        return await self.client.delete_channel(channel)

    async def fetch_guild(self, guild_id: str) -> Guild:
        """fetch details of a guild from khl"""
        guild = Guild(_gate_=self.client.gate, id=guild_id)
        await guild.load()
        return guild

    async def list_guild(self) -> List[Guild]:
        """list guilds the bot joined"""
        return await self.client.list_guild()

    @staticmethod
    async def send(target: Channel,
                   content: Union[str, List],
                   *,
                   type: MessageTypes = None,
                   temp_target_id: str = '',
                   **kwargs):
        """
        send a msg to a channel

        ``temp_target_id`` is only available in ChannelPrivacyTypes.GROUP
        """
        if isinstance(target, PublicTextChannel):
            kwargs['temp_target_id'] = temp_target_id

        return await target.send(content, type=type, **kwargs)

    async def upload_asset(self, file: Union[IO, str]) -> str:
        """DEPRECATED, will be removed in a future release: use ``create_asset()`` instead

        upload ``file`` to khl, and return the url to the file, alias for ``create_asset``

        if ``file`` is a str, ``open(file, 'rb')`` will be called to convert it into IO"""
        log.info('CAUTION: Bot.upload_asset() is DEPRECATED, please use create_asset() instead')
        return await self.create_asset(file)

    async def create_asset(self, file: Union[IO, str]) -> str:
        """upload ``file`` to khl, and return the url to the file

        if ``file`` is a str, ``open(file, 'rb')`` will be called to convert it into IO"""
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

    @staticmethod
    async def add_reaction(msg: Message, emoji: str):
        """add emoji to msg's reaction list

        wraps `Message.add_reaction`

        :param msg: accepts `Message`
        :param emoji: 😘
        """
        return await msg.add_reaction(emoji)

    @staticmethod
    async def delete_reaction(msg: Message, emoji: str, user: User = None):
        """delete emoji from msg's reaction list

        wraps `Message.delete_reaction`

        :param msg: accepts `Message`
        :param emoji: 😘
        :param user: whose reaction, delete others added reaction requires channel msg admin permission
        """
        return await msg.delete_reaction(emoji, user)

    async def list_game(self,
                        *,
                        begin_page: int = 1,
                        end_page: int = None,
                        page_size: int = 50,
                        sort: str = '') -> List[Game]:
        return await self.client.list_game(begin_page=begin_page, end_page=end_page, page_size=page_size, sort=sort)

    async def create_game(self, name: str, process_name: str = None, icon: str = None) -> Game:
        """
        
        Create a new game

        """
        return await self.client.create_game(name, process_name, icon)

    async def update_game(self, id: int, name: str = None, icon: str = None) -> Game:
        """

        Update game

        """
        return await self.client.update_game(id, name, icon)

    async def delete_game(self, game: Union[Game, int]):
        """

        Delete game

        :param game: accepts both Game object and bare id(int type)

        """
        await self.client.delete_game(game)

    async def update_playing_game(self, game: Union[Game, int]):
        """

        update current playing game status

        :param game: accepts both Game object and bare id(int type)
        :param data_type: 1 in default(means playing type is game)

        """
        await self.client.update_playing_game(game)

    async def stop_playing_game(self):
        """

        clear current playing game status

        """
        await self.client.stop_playing_game()

    async def update_listening_music(self, music_name:str, singer:str, software:Union[str, SoftwareTypes]):
        """

        update current listening music status

        :param music_name: name of music
        :param singer: singer of the music
        :param software: set software to playing the music
        :param data_type: 2 in default(means playing type is music)

        """
        await self.client.update_listening_music(music_name, singer, software)

    async def stop_listening_music(self):
        """

        clear current listening music status

        """
        await self.client.stop_listening_music()

    async def update_channel(self, channel: Union[str, PublicChannel], name: str = None, topic: str = None, slow_mode: Union[int, SlowModeTypes] = None):
        """
        update channel's settings
        """
        channel_id = channel if isinstance(channel, str) else channel.id
        await self.client.update_channel(channel_id, name, topic, slow_mode)

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
