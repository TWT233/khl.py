"""ABC"""
import asyncio
from abc import ABC, abstractmethod


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
