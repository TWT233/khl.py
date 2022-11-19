import logging

from apscheduler.events import EVENT_JOB_ERROR
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger

from khl import AsyncRunnable

log = logging.getLogger(__name__)


class TaskManager(AsyncRunnable):
    """manage tasks"""
    _scheduler: AsyncIOScheduler

    def __init__(self):
        self._scheduler = AsyncIOScheduler()

    def add_interval(self,
                     weeks=0,
                     days=0,
                     hours=0,
                     minutes=0,
                     seconds=0,
                     start_date=None,
                     end_date=None,
                     timezone=None,
                     jitter=None):
        """decorator, add a interval type task"""
        trigger = IntervalTrigger(weeks=weeks,
                                  days=days,
                                  hours=hours,
                                  minutes=minutes,
                                  seconds=seconds,
                                  start_date=start_date,
                                  end_date=end_date,
                                  timezone=timezone,
                                  jitter=jitter)
        return lambda func: self._scheduler.add_job(func, trigger)

    def add_cron(self,
                 year=None,
                 month=None,
                 day=None,
                 week=None,
                 day_of_week=None,
                 hour=None,
                 minute=None,
                 second=None,
                 start_date=None,
                 end_date=None,
                 timezone=None,
                 jitter=None):
        """decorator, add a cron type task"""
        trigger = CronTrigger(year=year,
                              month=month,
                              day=day,
                              week=week,
                              day_of_week=day_of_week,
                              hour=hour,
                              minute=minute,
                              second=second,
                              start_date=start_date,
                              end_date=end_date,
                              timezone=timezone,
                              jitter=jitter)
        return lambda func: self._scheduler.add_job(func, trigger)

    def add_date(self, run_date=None, timezone=None):
        """decorator, add a date type task"""
        trigger = DateTrigger(run_date=run_date, timezone=timezone)
        return lambda func: self._scheduler.add_job(func, trigger)

    async def start(self):
        self._scheduler.configure({'event_loop': self.loop}, '')
        self._scheduler.add_listener(lambda e: log.exception('error raised during task', exc_info=e.exception),
                                     EVENT_JOB_ERROR)
        self._scheduler.start()  # reminder: this is not blocking

    @property
    def scheduler(self):
        """getter, get the scheduler"""
        return self._scheduler
