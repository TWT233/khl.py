r"""Some Interfaces"""
import asyncio
from abc import ABC


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
