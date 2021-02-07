import asyncio
import logging
from typing import Coroutine, Iterable, Callable, TYPE_CHECKING, Set, List

from khl.message import Msg

if TYPE_CHECKING:
    pass


class Command:
    """
    Command, used in interaction from bots
    """
    name = ''
    handler = None
    trigger = ['']
    help = ''
    desc = ''
    logger = logging.getLogger('khl.Command')

    def __init__(self, func: Callable[..., Coroutine], name: str,
                 aliases: Iterable[str], help_doc: str, desc_doc: str):
        self.name: str
        self.handler: Callable[..., Coroutine]
        self.trigger: Set[str]
        self.help: str
        self.desc: str

        if not asyncio.iscoroutinefunction(func):
            raise TypeError('handler must be a coroutine.')
        self.handler = func

        self.name = name or func.__name__
        if not isinstance(self.name, str):
            raise TypeError('Name of a command must be a string.')

        self.trigger = set([i for i in aliases if isinstance(i, str)])
        self.trigger.add(self.name)

        self.help = help_doc
        if not isinstance(self.help, str):
            raise TypeError('help_doc must be a string.')

        self.desc = desc_doc
        if not isinstance(self.desc, str):
            raise TypeError('desc_doc must be a string.')

    async def execute(self, msg: Msg, *args):
        self.logger.debug(f'msg.content={msg.content} args={args}')
        return await self.handler(msg, *args)

    @staticmethod
    def command(name: str = '',
                aliases: Iterable[str] = (),
                help_doc: str = '',
                desc_doc: str = ''):
        """
        decorator to wrap a func into a Command

        :param name: the name of this Command, also used to trigger
        :param aliases: the aliases, used to trigger Command
        :param help_doc: detailed manual
        :param desc_doc: short introduction
        :return: wrapped Command
        """
        def decorator(func):
            return Command(func, name, aliases, help_doc, desc_doc)

        return decorator


class CommandGroup(Command):
    def __init__(self,
                 name: str,
                 aliases: Iterable[str] = (),
                 help_doc: str = '',
                 desc_doc: str = ''):
        self._sub_commands: Set[Command] = set()
        super().__init__(self.__gen_handler(), name, aliases, help_doc,
                         desc_doc)

    def __gen_handler(self):
        async def __handler(msg: Msg, *args):
            args = args[1:]
            for app in self._sub_commands:
                if args[0] in app.trigger:
                    await app.execute(msg, *args)

        return __handler

    def add_subcommand(self, cmd: Command):
        self._sub_commands.add(cmd)

    def subcommand(self,
                   name: str = '',
                   aliases: Iterable[str] = (),
                   help_doc: str = '',
                   desc_doc: str = ''):
        """
        decorator to wrap a func into a SubCommand

        :param name: the name of this SubCommand, also used to trigger
        :param aliases: the aliases, used to trigger
        :param help_doc: detailed manual
        :param desc_doc: short introduction
        :return: wrapped Command
        """
        def decorator(func):
            cmd = Command(func, name, aliases, help_doc, desc_doc)
            self.add_subcommand(cmd)

        return decorator
