import asyncio
import logging
from typing import Dict

log = logging.getLogger(__name__)


class RateLimiter:
    """rate limit control
    @param start: when the remain reach this number, start ratelimit
    """

    def __init__(self, start: int = 120):
        self._ratelimit_info: Dict[str, RateLimiter.RateLimitData] = {}
        self._api_bucket_mapping: Dict[str, str] = {}
        self._lock = asyncio.Lock()
        self._start = start

    async def wait_for_rate(self, route):
        """get and wait delay"""

        bucket = await self.get_bucket(route)
        delay = await self.get_delay(bucket)
        log.debug(f'ratelimiter: {route} req bucket: {bucket} delay: {delay: .3f}s')
        await asyncio.sleep(delay)

    async def update(self, route, headers):
        """get values and update ratelimit information"""

        if 'X-Rate-Limit-Limit' in headers:
            bucket, remaining, reset = self.extract_xrate_header(headers)
            await self.push_api_bucket_mapping(route, bucket)
            await self.update_ratelimit(bucket, remaining, reset)
            log.debug(f'ratelimiter: {route} rsp ratelimit: bucket: {bucket} remaining: {remaining} reset: {reset}s')

    async def push_api_bucket_mapping(self, api: str, bucket: str):
        """
        when finished request, associate bucket that api returned with api route
        to avoid that bucket and api router are not the same
        """

        api = api.lower()
        bucket = bucket.lower()

        async with self._lock:
            if api not in self._api_bucket_mapping:
                self._api_bucket_mapping[api] = bucket

    async def get_bucket(self, api: str):
        """get bucket name by api route"""

        api = api.lower()

        async with self._lock:
            if api not in self._api_bucket_mapping:
                return api

        return self._api_bucket_mapping[api]

    async def update_ratelimit(self, bucket: str, remaining: int, reset: int):
        """update rate limit info"""

        bucket = bucket.lower()
        async with self._lock:
            if bucket not in self._ratelimit_info:
                self._ratelimit_info[bucket] = self.RateLimitData(remaining, reset)
            else:
                self._ratelimit_info[bucket].remaining = remaining
                self._ratelimit_info[bucket].reset = reset

    async def get_delay(self, bucket: str) -> float:
        """get request delay time, seconds"""

        bucket = bucket.lower()
        async with self._lock:
            if bucket not in self._ratelimit_info:
                return 0

            if self._ratelimit_info[bucket].reset == 0:
                return 0

            if self._ratelimit_info[bucket].remaining == 0:
                return self._ratelimit_info[bucket].reset

            if self._ratelimit_info[bucket].remaining > self._start:
                return 0

            delay = self._ratelimit_info[bucket].reset / self._ratelimit_info[bucket].remaining

        return delay

    @staticmethod
    def extract_xrate_header(headers):
        """get bucket, remaining, reset values from headers"""

        bucket = headers['X-Rate-Limit-Bucket']
        remaining = int(headers['X-Rate-Limit-Remaining'])
        reset = int(headers['X-Rate-Limit-Reset'])
        return bucket, remaining, reset

    class RateLimitData:
        """to save single bucket rate limit"""

        def __init__(self, remaining: int = 120, reset: int = 0):
            self.remaining = remaining
            self.reset = reset
