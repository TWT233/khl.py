import asyncio
import logging
from typing import Optional, List, Union, Pattern, Dict, Any

from khl import Message, Client
from .command import Command
from .exception import TypeEHandler
from .lexer import Lexer, DefaultLexer
from .parser import Parser
from .rule import TypeRule

log = logging.getLogger(__name__)


class CommandManager:
    """aggregates commands as a system, and provide API as a whole"""
    _cmd_map: Dict[str, Command]

    def __init__(self):
        self._cmd_map = {}

    # why disable duplicate-code:
    # the duplicated code is the param list, used to provide auto complete/coding hints in IDE
    # pylint: disable = duplicate-code
    def __call__(
            self,
            name: str = '',
            *,
            help: str = '',
            desc: str = '',
            aliases: List[str] = (),
            prefixes: List[str] = ('/', ),
            regex: Union[str, Pattern] = '',
            lexer: Lexer = None,
            parser: Parser = None,
            rules: List[TypeRule] = (),
            exc_handlers: Dict[Any, TypeEHandler] = None,
    ):
        """
        decorator, wrap a function in Command and register it on current Bot

        :param name: the name of this Command, also used to trigger command in DefaultLexer
        :param aliases: (DefaultLexer only) you can also trigger the command with aliases
        :param prefixes: (DefaultLexer only) command prefix, default use '/'
        :param regex: (RELexer only) pattern for the command
        :param help: detailed manual
        :param desc: short introduction
        :param lexer: (Advanced) explicitly set the lexer
        :param parser: (Advanced) explicitly set the parser
        :param rules: only be executed if all rules are met
        :return: wrapped Command
        """
        args = {
            'help': help,
            'desc': desc,
            'aliases': aliases,
            'prefixes': prefixes,
            'regex': regex,
            'lexer': lexer,
            'parser': parser,
            'rules': rules,
            'exc_handlers': exc_handlers
        }

        return lambda func: self.add(Command.command(name, **args)(func))

    def add(self, command: Command) -> Command:
        """register the cmd on current Bot

        :param command: the Command going to be registered
        :return: the cmd
        """
        self[command.name] = command
        return command

    def get(self, name: str) -> Optional[Command]:
        """get command by name"""
        return self[name]

    def pop(self, name: str) -> Optional[Command]:
        """pop a command from Manager, return None if not exist"""
        cmd = self[name]
        if cmd:
            del self._cmd_map[name]
        return cmd

    async def handle(self, loop, client: Client, msg: Message, filter_args: dict):
        """pass msg into all commands in self, handle it concurrently"""
        for cmd in self._cmd_map.values():
            asyncio.ensure_future(cmd.handle(msg, client, filter_args), loop=loop)

    def update_prefixes(self, *prefixes: str) -> List[Command]:
        """update command prefixes in the Manager if command uses DefaultLexer

        :return: updated commands
        """
        prefixes = set(prefixes)
        updated = []
        for _, cmd in self.items():
            if not isinstance(cmd.lexer, DefaultLexer):
                continue
            cmd.lexer.prefixes = prefixes
            updated.append(cmd)
        return updated

    def __setitem__(self, name: str, cmd: Command):
        if cmd.name in self._cmd_map:
            raise ValueError(f'cmd: {cmd.name} already exists')
        self._cmd_map[cmd.name] = cmd
        log.debug(f'command: {cmd.name} added')

    def __getitem__(self, item) -> Optional[Command]:
        return self._cmd_map.get(item, None)

    def __iter__(self):
        return iter(self._cmd_map)

    def items(self):
        """all commands in self, keyed by command name"""
        return self._cmd_map.items()
