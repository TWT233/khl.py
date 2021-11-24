import asyncio
from datetime import timedelta, datetime
from typing import Optional, Coroutine, Callable

from .task import Task


class IntervalTask(Task):
    func: Callable[[], Coroutine]

    _interval: timedelta
    _next_run_at: Optional[datetime]
    _is_run_immediately: bool
    _is_running: bool

    def __init__(self, func: Callable[[], Coroutine], interval: timedelta, run_immediately: bool):
        self.func = func
        self._interval = interval
        self._is_run_immediately = run_immediately
        self._next_run_at = None
        self._is_running = False

    @classmethod
    def make(cls, interval: timedelta, *, run_immediately: bool = True):
        return lambda func: IntervalTask(func, interval, run_immediately)

    @property
    def interval(self) -> timedelta:
        return self._interval

    @property
    def next(self) -> datetime:
        if not self._is_running:
            raise RuntimeError('this task is not running')
        return self._next_run_at

    def _once(self, loop, run_at: datetime):
        asyncio.ensure_future(self.func(), loop=loop)
        self._next_run_at = run_at + self.interval

    async def run(self):
        if self._is_running:
            raise RuntimeError('this task is already running')
        self._is_running = True

        if self._is_run_immediately:
            self._once(self.loop, datetime.now())
        else:
            self._next_run_at = datetime.now() + self.interval

        while True:
            delay = (self._next_run_at - datetime.now()).total_seconds()
            await asyncio.sleep(delay)
            self._once(self.loop, self._next_run_at)
