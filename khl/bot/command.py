import asyncio
import logging
from typing import Callable, Coroutine, List, Any, Union, Pattern

from .lexer import Lexer, RELexer, DefaultLexer
from .parser import Parser
from ..message import Message

log = logging.getLogger(__name__)


class Command:
    """
    Receive a `Message`, parse it with `lex` and `parser`, execute `handler` if successfully parsed else discard it
    """
    name: str
    handler: Callable[..., Coroutine]
    help: str
    desc: str

    lexer: Lexer
    parser: Parser

    rules: List[Callable]

    def __init__(self, name: str, handler: Callable, help: str, desc: str, lexer: Lexer, parser: Parser,
                 rules: List[Callable] = ()):
        if not asyncio.iscoroutinefunction(handler):
            raise TypeError('handler must be a coroutine.')
        self.handler = handler

        self.name = name or handler.__name__
        if not isinstance(self.name, str):
            raise TypeError('Name of a command must be a string.')

        self.help = help
        self.desc = desc

        self.lexer = lexer
        self.parser = parser
        self.rules = list(rules)

    def _lex(self, msg: Message) -> List[str]:
        return self.lexer.lex(msg)

    def _parse(self, tokens: List[str], handler: Callable) -> List[Any]:
        return self.parser.parse(tokens, handler)

    async def _execute_rules(self, msg: Message, *args):
        result = True
        for rule in self.rules:
            try:
                result = result and await self._wrap_rule(rule, msg, *args)
            except Exception as e:
                log.exception(f"_execute_rules: {e}")
                return False
        return result

    @staticmethod
    async def _wrap_rule(rule, msg: Message, *args):
        if asyncio.iscoroutinefunction(rule):
            return await rule(msg, *args) is not None
        else:
            return rule(msg, *args) is not None

    def prepare(self, msg: Message) -> List[Any]:
        """
        parse msg, prepare arg list from the msg

        :param msg: the msg going to be lexed and parsed
        :return:
        """
        tokens = self._lex(msg)
        args = self._parse(tokens, self.handler)
        return args

    async def execute(self, msg: Message, *args):
        """
        pass msg and args from prepare() to handler()

        :param msg:
        :param args: the returned list of prepare()
        :return:
        """
        log.info(f'command {self.name} was triggered by msg: {msg.content}')
        try:
            if await self._execute_rules(msg, *args):
                await self.handler(msg, *args)
        except Exception as e:
            log.exception(f"execute: {Command.ExecuteException(self.handler, e)}")

    def do(self, msg: Message):
        """
        wrapper for prepare() and execute()

        :param msg: what wanna be handled
        """
        self.execute(msg, self.prepare(msg))

    @staticmethod
    def command(name: str = '', *, help: str = '', desc: str = '',
                aliases: List[str] = (), prefixes: List[str] = ('/',), regex: Union[str, Pattern] = '',
                lexer: Lexer = None, parser: Parser = None, rules: List[Callable]):
        """
        decorator, to wrap a func into a Command

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
        if not lexer and regex:
            lexer = RELexer(regex)

        # use lambda cuz i do not wanna declare decorator() explicitly to take 3 blank lines
        # did not init Lexer in advance cuz it needs func.__name__
        # this is redundant stuff in constructor, there should be a better way
        return lambda func: Command(name, func, help, desc,
                                    lexer or DefaultLexer(set(prefixes), set([name or func.__name__] + list(aliases))),
                                    parser or Parser(), rules)

    class ExecuteException(Exception):
        def __init__(self, func, e):
            self.func = func
            self.exception = e
