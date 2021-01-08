from abc import abstractmethod


class BaseClient:
    """ abstract base class, used as http wrapper
    """

    def __init__(self, port):
        self.type = ""
        self.port = port

    @abstractmethod
    async def send(self, url: str, data):
        """ send `data` to `url` """
        pass

    @abstractmethod
    def on_recv_append(self, callback):
        """ append callback to on_recv listener list """
        pass

    @abstractmethod
    def run(self):
        """ run client """
        pass
