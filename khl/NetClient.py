from abc import abstractmethod


class BaseClient:
    """
    http wrapper, including server and client

    abstract base class
    recv raw data from server, resolve request data and msg data from raw, pass it to inner context such as bot
    """

    def __init__(self, port):
        self.type = ""
        self.port = port

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
    def on_recv_append(self, callback):
        """
        append callback to on_recv listener list, callback accepts msg data from server

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
