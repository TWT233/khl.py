import asyncio
import logging
from typing import Dict
import aio_pika
from aio_pika.abc import AbstractExchange, AbstractRobustConnection
from . import RabbitMQ
from ..cert import Cert
from ..receiver import WebhookReceiver, WebsocketReceiver
from ..interface import AsyncRunnable
log = logging.getLogger(__name__)

class RabbitMQProducer(AsyncRunnable):
    """produce data to rabbitmq"""
    _exchange: AbstractExchange
    _connection: AbstractRobustConnection
    def __init__(self, rabbitmq: RabbitMQ):
        super().__init__()
        self._rabbitmq = rabbitmq
    async def start(self):
        self._exchange = await self._rabbitmq.get_exchange()
        while True:
            await asyncio.sleep(3600)  # sleep forever
    async def publish(self, data: dict):
        """produce data"""
        await self._exchange.publish(aio_pika.Message(body=self._rabbitmq.encode(data)),
                                     routing_key=self._rabbitmq.queue)

class RabbitMQProductionBot(AsyncRunnable):
    """
    This bot class is made for rabbitmq data production, to send package unwrapped by Receiver to rabbitmq
    """
    def __init__(self,
                 token: str = '',
                 *,
                 cert: Cert = None,
                 compress: bool = True,
                 port=5000,
                 route='/khl-wh',
                 rabbitmq: RabbitMQ = None):
        """
        :param cert: used to build requester and receiver
        :param compress: used to tune the receiver
        :param port: used to tune the WebhookReceiver
        :param route: used to tune the WebhookReceiver
        :param rabbitmq: used to tune the RabbitMQ Receiver or Producer
        """
        if not token and not cert:
            raise ValueError('require token or cert')

        if rabbitmq is None:
            raise ValueError('require rabbitmq')

        cert = cert or Cert(token=token)

        if cert.type == Cert.Types.WEBSOCKET:
            receiver = WebsocketReceiver(cert, compress)
        elif cert.type == Cert.Types.WEBHOOK:
            receiver = WebhookReceiver(cert, port=port, route=route, compress=compress)
        else:
            raise ValueError(f'cert type: {cert.type} not supported')

        self._pkg_queue = asyncio.Queue()
        self._receiver = receiver
        self._producer = RabbitMQProducer(rabbitmq)


    async def publish_pkg_to_rabbitmq(self):
        """publish pkg to rabbitmq"""
        while True:
            pkg: Dict = await self._pkg_queue.get()
            log.debug(f'publishing pkg: {pkg}')
            try:
                await self._producer.publish(pkg)
            except Exception as e:
                log.exception(e)
            self._pkg_queue.task_done()

    async def start(self):
        """start the rabbitmq bot"""
        self._receiver.pkg_queue = self._pkg_queue  # pass the pkg_queue to the receiver
        await asyncio.gather(self.publish_pkg_to_rabbitmq(), self._receiver.start(), self._producer.start())

    # keep the usage compatible with Bot interface, so ignored pylint warning
    # pylint: disable=duplicate-code
    def run(self):
        """run the rabbitmq bot in blocking mode"""
        if not self.loop:
            self.loop = asyncio.get_event_loop()
        try:
            self.loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            log.info('see you next time')
    # pylint: enable=duplicate-code
