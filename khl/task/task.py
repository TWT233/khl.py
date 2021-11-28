from abc import ABC, abstractmethod

from ..interface import AsyncRunnable


class Task(AsyncRunnable, ABC):

    @abstractmethod
    async def run(self):
        """the entry of the task"""
        ...
