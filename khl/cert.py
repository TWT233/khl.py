import base64
import json
from enum import Enum

from Cryptodome.Cipher import AES
from Cryptodome.Util import Padding


class Cert:
    """
    permission certification

    used in auth/data encrypt/decrypt
    """

    class Types(Enum):
        """
        types of :class:`Cert`

        used in extinguishing Cert and construct corresponding net client
        """
        NOTSET = 'not_set'
        WEBSOCKET = 'websocket'
        """
        websocket cert
        """
        WEBHOOK = 'webhook'
        """
        webhook cert
        """

    def __init__(self, *, type: Types = Types.NOTSET, token: str, verify_token: str = '', encrypt_key: str = ''):
        """
        all fields from bot config panel
        """
        if type != Cert.Types.NOTSET:
            self.type = type
        else:
            if verify_token:
                self.type = self.Types.WEBHOOK
            else:
                self.type = self.Types.WEBSOCKET
        self.token = token
        self.verify_token = verify_token
        self.encrypt_key = encrypt_key

    def decrypt(self, data: bytes) -> str:
        """ decrypt data

        :param data: encrypted byte array
        :return: decrypted str
        """
        if not self.encrypt_key:
            return ''
        data = base64.b64decode(data)
        data = AES.new(key=self.encrypt_key.encode().ljust(32, b'\x00'), mode=AES.MODE_CBC,
                       iv=data[0:16]).decrypt(base64.b64decode(data[16:]))
        data = Padding.unpad(data, 16)
        return data.decode('utf-8')

    def decode_raw(self, data: bytes) -> dict:
        data = json.loads(str(data, encoding='utf-8'))
        return json.loads(self.decrypt(data['encrypt'])) if ('encrypt' in data.keys()) else data
