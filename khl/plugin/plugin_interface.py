from ..bot import Bot


class PluginInterface:
    def __init__(self, token: str) -> None:
        self.token = token
        self.bot = Bot(token)
