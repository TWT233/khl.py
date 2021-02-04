from typing import NamedTuple

from khl.message import Msg


class BotSendArgs(NamedTuple):
    content: str
    quote: str
    type: Msg.Types
    nonce: str
