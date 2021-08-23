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
    merge_args = False
    rule = Callable[..., Coroutine]
    logger = logging.getLogger('khl.Command')

    def __init__(self, func: Callable[..., Coroutine], name: str,
                 aliases: Iterable[str], help_doc: str, desc_doc: str,
                 merge_args: bool, rule: Callable[..., Coroutine]):
        self.name: str
        self.handler: Callable[..., Coroutine]
        self.trigger: Set[str]
        self.help: str
        self.desc: str
        self.merge_args: bool
        self.rule: Callable[..., Coroutine]

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

        self.merge_args = merge_args
        if not isinstance(self.merge_args, bool):
            raise TypeError('merge_args must be a bool.')

        if not asyncio.iscoroutinefunction(rule):
            raise TypeError('rule must be a coroutine.')
        self.rule = rule

    def __merge_args(self, *args):
        params_count = self.handler.__code__.co_argcount - 1
        if params_count != 0:
            if len(args) > params_count:
                last_parameter = args[params_count - 1:]
                args = args[:params_count - 1] + tuple(
                    [" ".join(last_parameter)])
        return args

    async def __execute_rule(self, msg: Msg, *args):
        if self.rule is None:
            return True
        else:
            return await self.rule(msg, *args)

    async def execute(self, msg: Msg, *args):
        if await self.__execute_rule(msg, *args):
            self.logger.debug(f'msg.content={msg.content} args={args}')
            if self.merge_args:
                args = self.__merge_args(*args)
                return await self.handler(msg, *args)
            else:
                return await self.handler(msg, *args)

    @staticmethod
    def command(name: str = '',
                aliases: Iterable[str] = (),
                help_doc: str = '',
                desc_doc: str = '',
                merge_args: bool = False,
                rule: Callable[..., Coroutine] = None):
        """
        decorator to wrap a func into a Command

        :param name: the name of this Command, also used to trigger
        :param aliases: the aliases, used to trigger Command
        :param help_doc: detailed manual
        :param desc_doc: short introduction
        :param merge_args: merge redundant parameters,useful when the number of parameters is uncertain
        :param rule: restrictions are triggered only under certain rule
        :return: wrapped Command
        """

        def decorator(func):
            return Command(func, name, aliases, help_doc, desc_doc, merge_args, rule)

        return decorator


class CommandGroup(Command):
    def __init__(self,
                 name: str,
                 aliases: Iterable[str] = (),
                 help_doc: str = '',
                 desc_doc: str = '',
                 merge_args: bool = False,
                 rule: Callable[..., Coroutine] = None):
        self._sub_commands: Set[Command] = set()
        super().__init__(self.__gen_handler(), name, aliases, help_doc,
                         desc_doc, merge_args, rule)

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
                   desc_doc: str = '',
                   merge_args: bool = False,
                   rule: Callable[..., Coroutine] = None):
        """
        decorator to wrap a func into a SubCommand

        :param name: the name of this SubCommand, also used to trigger
        :param aliases: the aliases, used to trigger
        :param help_doc: detailed manual
        :param desc_doc: short introduction
        :param merge_args: merge redundant parameters(tail), same as *tail + ' '.join(tail)
        :param rule: restrictions are triggered only under certain rule
        :return: wrapped Command
        """

        def decorator(func):
            cmd = Command(func, name, aliases, help_doc, desc_doc, merge_args, rule)
            self.add_subcommand(cmd)

        return decorator
