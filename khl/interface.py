r"""Some Interfaces"""
import asyncio
from abc import ABC, abstractmethod
from enum import IntEnum, Enum


class AsyncRunnable(ABC):
    """
    Classes that has async work to run
    """
    _loop: asyncio.AbstractEventLoop = None

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """the event loop for the async work"""
        return self._loop

    @loop.setter
    def loop(self, new_loop: asyncio.AbstractEventLoop):
        self._loop = new_loop

    def schedule(self):
        """schedule the async work into background"""
        asyncio.ensure_future(self.start(), loop=self.loop)

    @abstractmethod
    async def start(self):
        """run the async work"""
        ...


class LazyLoadable(ABC):
    """
    Classes that can be initialized before loaded full data from khl server.
    These classes objects usually are constructed by khl.py internal calls.

    For example:
        `Channel`: we usually construct a channel with a message for convenient,
        while we only know the channel's id, so this channel is not `loaded`, until call the `load()`
    """
    _loaded: bool

    @abstractmethod
    async def load(self):
        """
        Load full data from khl server

        :return: empty
        """
        raise NotImplementedError

    @property
    def loaded(self) -> bool:
        """check if loaded"""
        return self._loaded

    @loaded.setter
    def loaded(self, v: bool):
        self._loaded = v

    def is_loaded(self) -> bool:
        """DEPRECATED: use ``.loaded`` prop, simpler in code and clearer in semantic
        Check if loaded

        :return: bool
        """
        return self._loaded


class MessageTypes(IntEnum):
    """
    types of message, type==SYS will be interpreted as `Event`, others are `Message`
    """
    TEXT = 1
    IMG = 2
    VIDEO = 3
    FILE = 4
    AUDIO = 8
    KMD = 9
    CARD = 10
    SYS = 255


class ChannelTypes(IntEnum):
    """
    types of channel
    """
    CATEGORY = 0
    TEXT = 1
    VOICE = 2


class ChannelPrivacyTypes(Enum):
    """
    channel's privacy level
    """
    GROUP = 'GROUP'
    PERSON = 'PERSON'


class EventTypes(Enum):
    """
    for system events(type==255)
    """
    MESSAGE_BTN_CLICK = 'message_btn_click'

    ADDED_REACTION = 'added_reaction'
    DELETED_REACTION = 'deleted_reaction'
    UPDATED_MESSAGE = 'updated_message'
    DELETED_MESSAGE = 'deleted_message'

    PRIVATE_ADDED_REACTION = 'private_added_reaction'
    PRIVATE_DELETED_REACTION = 'private_deleted_reaction'
    UPDATED_PRIVATE_MESSAGE = 'updated_private_message'
    DELETED_PRIVATE_MESSAGE = 'deleted_private_message'

    UPDATED_GUILD = 'updated_guild'
    DELETED_GUILD = 'deleted_guild'
    ADDED_BLOCK_LIST = 'added_block_list'
    DELETED_BLOCK_LIST = 'deleted_block_list'

    ADDED_ROLE = 'added_role'
    DELETED_ROLE = 'deleted_role'
    UPDATED_ROLE = 'updated_role'

    JOINED_GUILD = 'joined_guild'
    EXITED_GUILD = 'exited_guild'
    GUILD_MEMBER_ONLINE = 'guild_member_online'
    GUILD_MEMBER_OFFLINE = 'guild_member_offline'

    UPDATED_GUILD_MEMBER = 'updated_guild_member'

    UPDATED_CHANNEL = 'updated_channel'
    ADDED_CHANNEL = 'added_channel'
    DELETED_CHANNEL = 'deleted_channel'

    JOINED_CHANNEL = 'joined_channel'
    EXITED_CHANNEL = 'exited_channel'
    USER_UPDATED = 'user_updated'
    SELF_JOINED_GUILD = 'self_joined_guild'
    SELF_EXITED_GUILD = 'self_exited_guild'


class GuildMuteTypes(IntEnum):
    """
    types of guild-mute
    """
    MIC = 1
    HEADSET = 2
