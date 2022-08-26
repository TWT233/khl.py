"""abstraction of khl client: handle to communicate with khl"""
import asyncio
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Callable, Coroutine, Union, IO

from . import api
from .channel import public_channel_factory, PublicChannel, Channel, PublicTextChannel
from .game import Game
from .gateway import Gateway, Requestable
from .guild import Guild
from .interface import AsyncRunnable
from .message import RawMessage, Message, Event, PublicMessage, PrivateMessage
from ._types import SoftwareTypes, MessageTypes, SlowModeTypes
from .user import User
from .util import unpack_id, unpack_value

log = logging.getLogger(__name__)

TypeHandler = Callable[[Union['Message', 'Event']], Coroutine]


class Client(Requestable, AsyncRunnable):
    """
    The bridge between khl.py internal components and khl server.

    1. wraps net actions to khl backend, and translates raw objects into khl.py concepts/objects for internal use
    3. distributes package unwrapped by Receiver according to a handler map

    reminder: Client.loop only used to run handle_event() and registered handlers.
    """
    _handler_map: Dict[MessageTypes, List[TypeHandler]]

    def __init__(self, gate: Gateway):
        self.gate = gate
        self.ignore_self_msg = True
        self._me = None

        self._handler_map = {}
        self._pkg_queue = asyncio.Queue()

    def register(self, type: MessageTypes, handler: TypeHandler):
        """register handler to handle messages of type"""
        if not asyncio.iscoroutinefunction(handler):
            raise TypeError('handler must be a coroutine.')

        params = list(inspect.signature(handler).parameters.values())
        if len(params) != 1 or not issubclass(params[0].annotation, RawMessage):
            raise TypeError('handler must have one and only one param, and the param inherits RawMessage')

        if type not in self._handler_map:
            self._handler_map[type] = []
        self._handler_map[type].append(handler)

    async def handle_pkg(self):
        """consume `pkg` from `event_queue`"""
        while True:
            pkg: Dict = await self._pkg_queue.get()
            log.debug(f'upcoming pkg: {pkg}')

            try:
                await self._consume_pkg(pkg)
            except Exception as e:
                log.exception(e)

            self._pkg_queue.task_done()

    async def _consume_pkg(self, pkg: Dict):
        """
        spawn `msg` according to `pkg`,
        check if ignore msgs from self
        pass `msg` to corresponding handlers defined in `_handler_map`
        """
        msg = self._make_msg(pkg)
        if self.ignore_self_msg and msg.type != MessageTypes.SYS:
            if msg.author.id == (await self.fetch_me()).id:
                return
        self._dispatch_msg(msg)

    def _make_msg(self, pkg: Dict):
        if pkg.get('type') == MessageTypes.SYS.value:
            msg = Event(**pkg)
        else:
            msg = self._make_channel_msg(pkg)
        return msg

    def _make_channel_msg(self, pkg):
        msg = None
        channel_type = pkg.get('channel_type')
        if channel_type == 'GROUP':
            msg = PublicMessage(**pkg, _gate_=self.gate)
        elif channel_type == 'PERSON':
            msg = PrivateMessage(**pkg, _gate_=self.gate)
        else:
            log.error(f'can not make msg from pkg: {pkg}')
        return msg

    def _dispatch_msg(self, msg):
        if not msg:
            return
        handlers = self._handler_map.get(msg.type, ())
        for handler in handlers:
            asyncio.ensure_future(self._handle_safe(handler)(msg), loop=self.loop)

    @staticmethod
    def _handle_safe(handler: TypeHandler):

        async def safe_handler(msg):
            try:
                await handler(msg)
            except Exception as e:
                log.exception('error raised during message handling', exc_info=e)

        return safe_handler

    async def create_asset(self, file: Union[IO, str, Path]) -> str:
        """upload ``file`` to khl, and return the url to the file

        if ``file`` is a str or Path, ``open(file, 'rb')`` will be called to convert it into IO
        """
        if not isinstance(file, (str, Path)):
            return (await self.gate.exec_req(api.Asset.create(file=file)))['url']
        with open(file, 'rb') as f:
            return (await self.gate.exec_req(api.Asset.create(file=f)))['url']

    async def fetch_me(self, force_update: bool = False) -> User:
        """fetch detail of the ``User`` on the client"""
        if force_update or not self._me or not self._me.is_loaded():
            self._me = User(_gate_=self.gate, _lazy_loaded_=True, **(await self.gate.exec_req(api.User.me())))
        return self._me

    @property
    def me(self) -> User:
        """
        get client itself corresponding User

        RECOMMEND: use ``await fetch_me()``

        CAUTION: please call ``await fetch_me()`` first to load data from khl server

        designed as 'empty-then-fetch' will break the rule 'net-related is async'

        :return: the client's underlying User
        """
        if self._me and self._me.is_loaded():
            return self._me
        raise ValueError('not loaded, please call `await fetch_me()` first')

    async def fetch_public_channel(self, channel_id: str) -> PublicChannel:
        """fetch details of a public channel from khl"""
        channel_data = await self.gate.exec_req(api.Channel.view(channel_id))
        return public_channel_factory(_gate_=self.gate, **channel_data)

    async def fetch_user(self, user: Union[User, str]) -> User:
        """fetch detail of the specific user"""
        user_id = unpack_id(user)
        return User(_gate_=self.gate, _lazy_loaded_=True, **(await self.gate.exec_req(api.User.view(user_id))))

    async def fetch_guild(self, guild_id: str) -> Guild:
        """fetch details of a guild from khl"""
        guild = Guild(_gate_=self.gate, id=guild_id)
        await guild.load()
        return guild

    async def fetch_guild_list(self, **kwargs) -> List[Guild]:
        """list guilds which the client joined

        paged req, support standard pagination args"""
        guilds_data = (await self.gate.exec_paged_req(api.Guild.list(), **kwargs))
        return [Guild(_gate_=self.gate, _lazy_loaded_=True, **i) for i in guilds_data]

    async def leave(self, guild: Union[Guild, str]):
        """leave from ``guild``"""
        guild = Guild(_gate_=self.gate, id=guild) if isinstance(guild, str) else guild
        return await guild.leave()

    async def kickout(self, guild: Guild, user: Union[User, str]):
        """kick ``user`` out from ``guild``"""
        guild = Guild(_gate_=self.gate, id=guild) if isinstance(guild, str) else guild
        return await guild.kickout(user)

    async def delete_channel(self, channel: Union[Channel, str]):
        """delete a channel, permission required"""
        return await self.gate.exec_req(api.Channel.delete(unpack_id(channel)))

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

    async def fetch_game_list(self, **kwargs) -> List[Game]:
        """list the games already registered at khl server

        paged req, support standard pagination args"""
        games = await self.gate.exec_paged_req(api.game(), **kwargs)
        return [Game(**game_data) for game_data in games]

    async def register_game(self, name, process_name: str, icon: str) -> Game:
        """register a new game at khl server, can be used in profile status"""
        data = {
            'name': name,
        }
        if process_name is not None:
            data['process_name'] = process_name
        if icon is not None:
            data['icon'] = icon
        game_data = (await self.gate.exec_req(api.Game.create(**data)))
        return Game(**game_data)

    async def update_game(self, id: int, name: str, icon: str) -> Game:
        """update game already registered at khl server"""
        data = {'id': id}
        if name is not None:
            data['name'] = name
        if icon is not None:
            data['icon'] = icon
        game_data = (await self.gate.exec_req(api.Game.update(**data)))
        return Game(**game_data)

    async def unregister_game(self, game: Union[Game, int]):
        """unregister game from khl server

        :param game: accepts both Game object and bare game id(int type)
        """
        await self.gate.exec_req(api.Game.delete(id=unpack_id(game)))

    async def update_playing_game(self, game: Union[Game, int]):
        """update current playing game status

        :param game: accepts both Game object and bare id(int type)
        """
        await self.gate.exec_req(api.Game.activity(id=unpack_id(game), data_type=1))

    async def stop_playing_game(self):
        """clear current playing game status"""
        await self.gate.exec_req(api.Game.deleteActivity(data_type=1))

    async def update_listening_music(self, music_name: str, singer: str, software: Union[str, SoftwareTypes] = None):
        """update current listening music status

        :param music_name: such as 'Yesterday Once More'
        :param singer: such as 'Carpenters'
        :param software: music software, CLOUD_MUSIC as default
        """
        params = {'music_name': music_name, 'singer': singer, 'data_type': 2}
        if software:
            params['software'] = unpack_value(software)
        await self.gate.exec_req(api.Game.activity(**params))

    async def stop_listening_music(self):
        """clear current listening music status"""
        await self.gate.exec_req(api.Game.deleteActivity(data_type=2))

    async def update_channel(self,
                             channel: Union[str, PublicChannel],
                             name: str = None,
                             topic: str = None,
                             slow_mode: Union[int, SlowModeTypes] = None) -> PublicChannel:
        """update channel's settings"""
        channel = channel if isinstance(channel, PublicChannel) else await self.fetch_public_channel(channel)
        channel_data = await channel.update(name, topic, slow_mode)
        return public_channel_factory(_gate_=self.gate, **channel_data)

    async def start(self):
        await asyncio.gather(self.handle_pkg(), self.gate.run(self._pkg_queue))
