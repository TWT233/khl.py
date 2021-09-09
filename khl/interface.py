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
        return self._loop

    @loop.setter
    def loop(self, new_loop: asyncio.AbstractEventLoop):
        self._loop = new_loop


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

    def is_loaded(self) -> bool:
        """
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
