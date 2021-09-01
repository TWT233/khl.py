r"""Some Interfaces"""
import asyncio
from abc import ABC, abstractmethod


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

    async def is_loaded(self) -> bool:
        """
        Check if loaded

        :return: bool
        """
        return self._loaded