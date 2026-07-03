import asyncio
import logging
from typing import Dict
from ..receiver import Receiver
from .rabbitmq import RabbitMQ
log = logging.getLogger(__name__)


class RabbitMQReceiver(Receiver):
    """receive data in RabbitMQ mode"""
    def __init__(self, rabbitmq: RabbitMQ):
        super().__init__()
        self._rabbitmq = rabbitmq
    @property
    def type(self) -> str:
        return 'rabbitmq'
    async def start(self):
        queue = await self._rabbitmq.get_queue()
        log.info('[ init ] launched')
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        pkg: Dict = self._rabbitmq.decode(message.body)
                    except Exception as e:
                        log.exception(e)
                        continue
                    if not pkg:  # empty pkg
                        continue
                    while self.pkg_queue.qsize() >= self._rabbitmq.qos:
                        await asyncio.sleep(0.001)
                    await self.pkg_queue.put(pkg)
