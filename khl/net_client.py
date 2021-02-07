from abc import abstractmethod, ABC
from asyncio import Queue

from .cert import Cert


class BaseClient(ABC):
    """
    http wrapper, including server and client

    abstract base class
        1. recv raw data from server
        2. resolve request data and msg data from raw
        3. pass it to inner context such as bot
    """
    type: str
    event_queue: Queue
    cert: Cert

    def __init__(self):
        pass

    @abstractmethod
    async def run(self):
        """
        run client to listen req from server

        and push req into `req_queue`

        :return: None
        """
        pass
