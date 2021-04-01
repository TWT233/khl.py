import asyncio
import logging
from asyncio import Queue
from typing import Any, Dict


class KQueue:
    logger = logging.getLogger('khl.KQueue')

    def __init__(self) -> None:
        self._listeners: Dict[str, Queue] = {}
        self._ref_cnt: Dict[str, int] = {}

    async def get(self, key: str, timeout: float = 30) -> Any:
        if key not in self._listeners.keys():
            self._listeners[key] = Queue()
            self._ref_cnt[key] = 0

        self._ref_cnt[key] += 1

        try:
            res = await asyncio.wait_for(self._listeners[key].get(), timeout)
            self._listeners[key].task_done()
        except asyncio.TimeoutError:
            res = None

        self._ref_cnt[key] -= 1

        if self._ref_cnt[key] == 0:
            del self._listeners[key]
            del self._ref_cnt[key]

        return res

    async def put(self, key: str, item: Any):
        if key in self._listeners.keys():
            self.logger.debug(f'putting item into KQueue, item:\n{item}')
            await self._listeners[key].put(item)
