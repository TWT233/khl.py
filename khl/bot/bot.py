"""implementation of bot"""
import asyncio
import logging
import warnings
from pathlib import Path
from typing import Dict, Callable, List, Optional, Union, Coroutine, IO

from .. import AsyncRunnable  # interfaces
from .. import Cert, HTTPRequester, RateLimiter, WebhookReceiver, WebsocketReceiver, Gateway, Client  # net related
from .. import MessageTypes, EventTypes, SlowModeTypes, SoftwareTypes  # types
from .. import User, Channel, PublicChannel, Guild, Event, Message  # concepts
from ..command import CommandManager
from ..game import Game
from ..task import TaskManager

log = logging.getLogger(__name__)

TypeEventHandler = Callable[['Bot', Event], Coroutine]
TypeMessageHandler = Callable[[Message], Coroutine]
TypeStartupHandler = Callable[['Bot'], Coroutine]
TypeShutdownHandler = Callable[['Bot'], Coroutine]


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

    _startup_index: List[TypeStartupHandler]
    _shutdown_index: List[TypeShutdownHandler]

    def __init__(self,
                 token: str = '',
                 *,
                 cert: Cert = None,
                 client: Client = None,
                 gate: Gateway = None,
                 out: HTTPRequester = None,
                 compress: bool = True,
                 port=5000,
                 route='/khl-wh',
                 ratelimiter: Optional[RateLimiter] = RateLimiter(start=80)):
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

        self._init_client(cert or Cert(token=token), client, gate, out, compress, port, route, ratelimiter)
        self._register_client_handler()

        self.command = CommandManager()

        self.task = TaskManager()

        self._is_running = False
        self._event_index = {}
        self._startup_index = []
        self._shutdown_index = []

    def _init_client(self, cert: Cert, client: Client, gate: Gateway, out: HTTPRequester, compress: bool, port, route,
                     ratelimiter):
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
        _out = out if out else HTTPRequester(cert, ratelimiter)
        if cert.type == Cert.Types.WEBSOCKET:
            _in = WebsocketReceiver(cert, compress)
        elif cert.type == Cert.Types.WEBHOOK:
            _in = WebhookReceiver(cert, port=port, route=route, compress=compress)
        else:
            raise ValueError(f'cert type: {cert.type} not supported')

        self.client = Client(Gateway(_out, _in))

    def _register_client_handler(self):
        # text and kmd -> msg
        msg_handler = self._make_msg_handler()
        self.client.register(MessageTypes.TEXT, msg_handler)
        self.client.register(MessageTypes.KMD, msg_handler)

        # sys -> event
        self.client.register(MessageTypes.SYS, self._make_event_handler())

    def _make_msg_handler(self) -> Callable:
        """
        construct a function to receive msg from client, and interpret it with _cmd_index
        """

        async def handler(msg: Message):
            await self.command.handle(self.loop, self.client, msg, {Message: msg, Bot: self})

        return handler

    def _make_event_handler(self) -> Callable:

        async def handler(event: Event):
            if event.event_type not in self._event_index:
                return
            if not self._event_index[event.event_type]:
                return
            for event_handler in self._event_index[event.event_type]:
                await event_handler(self, event)

        return handler

    def add_event_handler(self, type: EventTypes, handler: TypeEventHandler):
        """add an event handler function for EventTypes `type`"""
        if type not in self._event_index:
            self._event_index[type] = []
        self._event_index[type].append(handler)
        log.debug(f'event_handler {handler.__qualname__} for {type} added')
        return handler

    def add_message_handler(self, handler: TypeMessageHandler, *except_type: MessageTypes):
        """`except_type` is an exclusion list"""
        for type in MessageTypes:
            if type not in except_type:
                self.client.register(type, handler)

    def on_event(self, type: EventTypes):
        """decorator, register a function to handle events of the type"""

        def dec(func: TypeEventHandler):
            self.add_event_handler(type, func)

        return dec

    def on_message(self, *except_type: MessageTypes):
        """
        decorator, register a function to handle messages
        :param except_type: excepted types
        """

        def dec(func: TypeMessageHandler):
            self.add_message_handler(func, *set(except_type + (MessageTypes.SYS, )))

        return dec

    def on_startup(self, func: TypeStartupHandler):
        """decorator, register a function to handle bot start"""

        self._startup_index.append(func)

        return func

    def on_shutdown(self, func: TypeShutdownHandler):
        """decorator, register a function to handle bot stop"""

        self._shutdown_index.append(func)

        return func

    async def fetch_me(self, force_update: bool = False) -> User:
        """fetch detail of the bot it self as a ``User``

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.fetch_me()`"""
        warnings.warn("deprecated, alternative: bot.client.fetch_me()", DeprecationWarning, stacklevel=2)
        return await self.client.fetch_me(force_update)

    @property
    def me(self) -> User:
        """
        get bot itself data

        CAUTION: please call ``await fetch_me()`` first to load data from khl server

        designed as 'empty-then-fetch' will break the rule 'net-related is async'

        :returns: the bot's underlying User

        .. deprecated-removed:: 0.3.0 0.4.0
            use await :func:`.client.fetch_me()`
        """
        warnings.warn("deprecated, alternative: bot.client.fetch_me(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return self.client.me

    async def fetch_public_channel(self, channel_id: str) -> PublicChannel:
        """channel id -> :class:`PublicChannel` object(public channel only),
        fetch details of a public channel from khl

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.fetch_public_channel()`"""
        warnings.warn("deprecated, alternative: bot.client.fetch_public_channel(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.fetch_public_channel(channel_id)

    async def fetch_user(self, user_id: str) -> User:
        """user id -> :class:`User` object, fetch user info from khl

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.fetch_user()`"""
        warnings.warn("deprecated, alternative: bot.client.fetch_user(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.fetch_user(user_id)

    async def delete_channel(self, channel: Union[Channel, str]):
        """delete a channel, permission required

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.delete_channel()`"""
        warnings.warn("deprecated, alternative: bot.client.delete_channel(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.delete_channel(channel)

    async def fetch_guild(self, guild_id: str) -> Guild:
        """guild id -> :class:`Guild` object, fetch details of a guild from khl

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.fetch_guild()`"""
        warnings.warn("deprecated, alternative: bot.client.fetch_guild(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.fetch_guild(guild_id)

    async def list_guild(self) -> List[Guild]:
        """list guilds the bot joined

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.fetch_guild_list()`
        """
        warnings.warn("deprecated, alternative: bot.client.fetch_guild_list(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.fetch_guild_list()

    async def send(self,
                   target: Channel,
                   content: Union[str, List],
                   *,
                   type: MessageTypes = None,
                   temp_target_id: str = '',
                   **kwargs):
        """
        send a msg to a channel

        ``temp_target_id`` is only available in ChannelPrivacyTypes.GROUP

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.send()`"""
        warnings.warn("deprecated, alternative: bot.client.send(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.send(target, content, type=type, temp_target_id=temp_target_id, **kwargs)

    async def upload_asset(self, file: Union[IO, str, Path]) -> str:
        """upload ``file`` to khl, and return the url to the file, alias for ``create_asset``

        if ``file`` is a str or Path, ``open(file, 'rb')`` will be called to convert it into IO

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.create_asset()`"""
        warnings.warn("deprecated, alternative: bot.client.create_asset(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.create_asset(file)

    async def create_asset(self, file: Union[IO, str, Path]) -> str:
        """upload ``file`` to khl, and return the url to the file

        if ``file`` is a str or Path, ``open(file, 'rb')`` will be called to convert it into IO

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.create_asset()`"""
        warnings.warn("deprecated, alternative: bot.client.create_asset(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.create_asset(file)

    async def kickout(self, guild: Union[Guild, str], user: Union[User, str]):
        """kick ``user`` out from ``guild``

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.kickout()`"""
        warnings.warn("deprecated, alternative: bot.client.kickout(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.kickout(guild, user)

    async def leave(self, guild: Union[Guild, str]):
        """leave from ``guild``

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.leave()`"""
        warnings.warn("deprecated, alternative: bot.client.leave(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.leave(guild)

    async def add_reaction(self, msg: Message, emoji: str):
        """add emoji to msg's reaction list

        wraps `Message.add_reaction`

        :param msg: accepts `Message`
        :param emoji: 😘

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.add_reaction()`
        """
        warnings.warn("deprecated, alternative: bot.client.add_reaction(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.add_reaction(msg, emoji)

    async def delete_reaction(self, msg: Message, emoji: str, user: User = None):
        """delete emoji from msg's reaction list

        wraps `Message.delete_reaction`

        :param msg: accepts `Message`
        :param emoji: 😘
        :param user: whose reaction, delete others added reaction requires channel msg admin permission

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.delete_reaction()`
        """
        warnings.warn("deprecated, alternative: bot.client.delete_reaction(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.delete_reaction(msg, emoji, user)

    async def list_game(self,
                        *,
                        begin_page: int = 1,
                        end_page: int = None,
                        page_size: int = 50,
                        sort: str = '') -> List[Game]:
        """list the games already registered at khl server

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.fetch_game_list()`"""
        warnings.warn("deprecated, alternative: bot.client.fetch_game_list(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.fetch_game_list(begin_page=begin_page,
                                                 end_page=end_page,
                                                 page_size=page_size,
                                                 sort=sort)

    async def create_game(self, name: str, process_name: str = None, icon: str = None) -> Game:
        """register a new game at khl server, can be used in profile status

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.register_game()`"""
        warnings.warn("deprecated, alternative: bot.client.register_game(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.register_game(name, process_name, icon)

    async def update_game(self, id: int, name: str = None, icon: str = None) -> Game:
        """update game already registered at khl server

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.update_game()`"""
        warnings.warn("deprecated, alternative: bot.client.update_game(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        return await self.client.update_game(id, name, icon)

    async def delete_game(self, game: Union[Game, int]):
        """unregister game from khl server

        :param game: accepts both Game object and bare game id(int type)

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.unregister_game()`"""
        warnings.warn("deprecated, alternative: bot.client.unregister_game(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        await self.client.unregister_game(game)

    async def update_playing_game(self, game: Union[Game, int]):
        """update current playing game status

        :param game: accepts both Game object and bare id(int type)

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.update_playing_game()`"""
        warnings.warn("deprecated, alternative: bot.client.update_playing_game(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        await self.client.update_playing_game(game)

    async def stop_playing_game(self):
        """clear current playing game status

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.stop_playing_game()`"""
        warnings.warn("deprecated, alternative: bot.client.stop_playing_game(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        await self.client.stop_playing_game()

    async def update_listening_music(self, music_name: str, singer: str, software: Union[str, SoftwareTypes]):
        """update current listening music status

        :param music_name: name of music
        :param singer: singer of the music
        :param software: set software to playing the music

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.update_listening_music()`"""
        warnings.warn("deprecated, alternative: bot.client.update_listening_music(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        await self.client.update_listening_music(music_name, singer, software)

    async def stop_listening_music(self):
        """clear current listening music status

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.stop_listening_music()`"""
        warnings.warn("deprecated, alternative: bot.client.stop_listening_music(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        await self.client.stop_listening_music()

    async def update_channel(self,
                             channel: Union[str, PublicChannel],
                             name: str = None,
                             topic: str = None,
                             slow_mode: Union[int, SlowModeTypes] = None):
        """update channel's settings

        .. deprecated-removed:: 0.3.0 0.4.0
            use :func:`.client.update_channel()`"""
        warnings.warn("deprecated, alternative: bot.client.update_channel(), everything else is in the same",
                      DeprecationWarning,
                      stacklevel=2)
        await self.client.update_channel(channel, name, topic, slow_mode)

    async def start(self):
        for func in self._startup_index:
            await func(self)
        if self._is_running:
            raise RuntimeError('this bot is already running')
        self.task.schedule()
        await self.client.start()

    def run(self):
        """run the bot in blocking mode"""
        if not self.loop:
            self.loop = asyncio.get_event_loop()
        try:
            self.loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            for func in self._shutdown_index:
                self.loop.run_until_complete(func(self))
            log.info('see you next time')
