import asyncio
import logging
from asyncio import Queue
from typing import Any, Coroutine, Dict


class KQueue:
    logger = logging.getLogger('khl.KQueue')

    def __init__(self) -> None:
        self._listeners: Dict[str, Queue] = {}
        self._ref_cnt: Dict[str, int] = {}
        self._futures: Dict[str, Coroutine] = {}

    async def get(self, key: str, timeout: float = 30) -> Any:
        """
        key: user id for user, msg id for button
        """
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

    async def get_latest(self, key: str, timeout: float = 30) -> Any:

        self._listeners[key] = Queue()
        if self._futures.get(key):
            self.logger.debug('found previous session, cancelling...')
            try:
                self._futures[key].close()
                self.logger.debug('cancelled previous session')
            except Exception:
                self.logger.exception('exception when cancelling session')

        self._futures[key] = self._listeners[key].get()

        res = None
        try:
            res = await asyncio.wait_for(self._futures[key], timeout)
            if self._futures[key].cr_frame is None:
                self.logger.debug(
                    '{key} is empty, deleting item'.format(key=key))
                del self._listeners[key]
                del self._futures[key]
        except asyncio.TimeoutError:
            res = None
        except AttributeError as e:
            self.logger.exception(e)
        except RuntimeError:
            raise RuntimeError('input is cancelled')

        return res
