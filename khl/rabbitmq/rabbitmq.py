import hashlib
import json
import logging
import zlib
import aio_pika
from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractExchange, AbstractRobustQueue
log = logging.getLogger(__name__)


class RabbitMQ:
    """rabbitmq configurate/init/connect/encrypt/decrypt/encode/decode"""
    _connection: AbstractRobustConnection = None
    _channel: AbstractRobustChannel = None
    _queue: AbstractRobustQueue = None
    _exchange: AbstractExchange = None
    def __init__(self, login: str, password: str, host: str = '127.0.0.1', port: int = 5672, queue: str = 'kook',
                 qos: int = 10, heartbeat: int = 30, key: str = '', salt: str = '', key_digits: int = 32,
                 compress: bool = True):
        self._host = host
        self._port = port
        self.queue = queue
        self.qos = qos
        self._heartbeat = heartbeat
        self._login = login
        self._password = password
        self.compress = compress
        # check aes is 128, 192 or 256
        if key_digits not in AES.key_size:
            raise ValueError(f'rabbitmq key_digits: {key_digits} not in {AES.key_size}')
        if key != '':
            key_string = key
        else:
            # if rabbitmq_key is not defined, use sha256 to generate one
            # construct a variable complex certain string
            # login, password, queue, compress, key_digits are same in both sides
            key_string = f'khl.py://{login}:{password}/{queue}?&compress={compress}&key_digits={key_digits}'

        if salt != '':
            salt_encoded = salt.encode('utf-8')
        else:
            salt_encoded = b'rabbitmq in khl.py'

        # use pbkdf2_hmac to generate key with key_digits
        self._aes_key = hashlib.pbkdf2_hmac(
            'sha256',
            key_string.encode('utf-8'),
            salt_encoded,
            100000,
            dklen=key_digits
        )

    def decrypt(self, data: bytes) -> bytes:
        """ decrypt data
        :param data: encrypted byte array
        :return: decrypted byte array
        """
        decipher = AES.new(self._aes_key, AES.MODE_CBC, iv=data[:16])
        data = decipher.decrypt(data[16:])
        data = Padding.unpad(data, 16)
        return data
    def encrypt(self, data: bytes) -> bytes:
        """ encrypt data
        :param data: byte array
        :return: encrypted byte array
        """
        data = Padding.pad(data, 16)
        cipher = AES.new(self._aes_key, AES.MODE_CBC)
        data = cipher.encrypt(data)
        return cipher.iv + data
    def decode(self, data: bytes) -> dict:
        """decode raw rabbitmq data into plaintext data"""
        data = self.decrypt(data)
        if self.compress:
            data = zlib.decompress(data)
        return json.loads(str(data, encoding='utf-8'))
    def encode(self, data: dict) -> bytes:
        """encode pkg into rabbitmq data"""
        data = json.dumps(data).encode(encoding='utf-8')
        if self.compress:
            data = zlib.compress(data)
        data = self.encrypt(data)
        return data
    async def get_connection(self) -> AbstractRobustConnection:
        """get rabbitmq connection"""
        if self._connection is None:
            self._connection = await aio_pika.connect_robust(
                host=self._host,
                port=self._port,
                login=self._login,
                password=self._password,
                heartbeat=self._heartbeat
            )
            await self._connection.connect()
        return self._connection
    async def get_channel(self) -> AbstractRobustChannel:
        """get rabbitmq channel"""
        if self._channel is None:
            connection = await self.get_connection()
            self._channel = await connection.channel()
        return self._channel
    async def get_queue(self) -> AbstractRobustQueue:
        """get rabbitmq queue"""
        if self._queue is None:
            channel = await self.get_channel()
            self._queue = await channel.declare_queue(self.queue)
        return self._queue
    async def get_exchange(self) -> AbstractExchange:
        """get rabbitmq default exchange"""
        if self._exchange is None:
            channel = await self.get_channel()
            self._exchange = channel.default_exchange
        return self._exchange
