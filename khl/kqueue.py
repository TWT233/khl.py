import logging
from asyncio import Queue
from typing import Any, Dict


class KQueue:
    logger = logging.getLogger('khl.KQueue')

    def __init__(self) -> None:
        self._listeners: Dict[str, Queue] = {}

    async def get(self, key: str) -> Any:
        if key not in self._listeners.keys():
            self._listeners[key] = Queue()
        res = await self._listeners[key].get()
        self._listeners[key].task_done()
        return res

    async def put(self, key: str, item: Any):
        if key in self._listeners.keys():
            self.logger.debug(f'putting item into KQueue, item:\n{item}')
            await self._listeners[key].put(item)
