from .channel import Channel
from .gateway import Requestable
from .guild import Guild


class Context(Requestable):
    channel: Channel
    guild: Guild

    def __init__(self, **kwargs):
        self.channel = kwargs.get('channel')
        self.guild = kwargs.get('guild')
        self.gate = kwargs.get('_gate_')
