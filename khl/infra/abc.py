r"""Some Interfaces"""

from abc import ABC, abstractmethod

from ..gateway import Gateway


class Requestable(ABC):
    """
    Classes that can use a `Gateway` to communicate with khl server.

    For example:
        `Message`: can use msg.reply() to send a reply to khl

        `Guild`: guild.get_roles() to fetch role list from khl
    """
    _gate: Gateway

    @property
    def gate(self) -> Gateway:
        """
        Getter for gate

        :return: Gateway that being used
        """
        return self._gate


class LazyLoadable(Requestable, ABC):
    """
    Classes that can be initialized before loaded full data from khl server.
    These classes objects usually are constructed by khl.py internal calls.

    For example:
        `Channel`: we usually construct a channel with a message for convenient,
        while we only know the channel's id, so this channel is not `loaded`, until call the `load()`

    """
    _loaded: bool

    @abstractmethod
    async def load(self):
        """
        Load full data from khl server

        :return: empty
        """
        raise NotImplementedError

    async def is_loaded(self) -> bool:
        """
        Check if loaded

        :return: bool
        """
        return self._loaded
