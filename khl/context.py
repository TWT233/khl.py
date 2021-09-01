from .gateway import Requestable
from .channel import Channel
from .guild import Guild


class Context(Requestable):
    channel: Channel
    guild: Guild

    def __init__(self, **kwargs):
        self.channel = kwargs.get('channel')
        self.guild = kwargs.get('guild')
        self._gate = kwargs.get('_gate_')
