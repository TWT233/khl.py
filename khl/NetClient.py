from abc import abstractmethod


class BaseClient:

    def __init__(self, port):
        self.type = ""
        self.port = port

    @abstractmethod
    async def send(self, url: str, data):
        pass

    @abstractmethod
    def on_recv_append(self, callback):
        pass

    @abstractmethod
    def run(self):
        pass
