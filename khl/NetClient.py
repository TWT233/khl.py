from abc import abstractmethod, ABC
from typing import Any, Callable, Coroutine, Dict


class BaseClient(ABC):
    """
    http wrapper, including server and client

    abstract base class
        1. recv raw data from server
        2. resolve request data and msg data from raw
        3. pass it to inner context such as bot
    """
    def __init__(self):
        self.type = ""

    @abstractmethod
    async def send(self, url: str, data):
        """
        send `data` to `url` with POST

        :param url: the destination
        :param data: payload
        :type data: dict or array
        :return: request result
        """
        pass

    @abstractmethod
    def on_recv_append(self, callback: Callable[[Dict[Any, Any]], Coroutine]):
        """
        append callback to on_recv listener list

        :param callback: handler that will be called on msg recv
        :type callback: function(e)->Any
        :return: None
        """
        pass

    @abstractmethod
    def run(self):
        """
        run client

        :return: None
        """
        pass
