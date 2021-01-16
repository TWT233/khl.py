from khl.Bot import Bot
from khl.Message import TextMsg
from typing import Iterable
from khl.command.app import App


class Session:
    command: App or str
    args: Iterable[str]
    msg: TextMsg
    bot: Bot

    def __init__(self,
                 command: App,
                 args: Iterable[str],
                 msg: TextMsg,
                 bot: Bot = None) -> None:
        super().__init__()
        self.command = command
        self.args = args
        self.msg = msg
        self.bot = bot if bot else self.command.bot

        
