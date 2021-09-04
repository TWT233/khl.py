import asyncio
import logging
from typing import Callable, Coroutine, List, Any

from .lexer import Lexer, ShlexLexer
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

    def __init__(self, name: str, handler: Callable[..., Coroutine], help: str, desc: str,
                 lexer: Lexer, prefixes: List[str], triggers: List[str],
                 parser: Parser):
        if not asyncio.iscoroutinefunction(handler):
            raise TypeError('handler must be a coroutine.')
        self.handler = handler

        self.name = name or handler.__name__
        if not isinstance(self.name, str):
            raise TypeError('Name of a command must be a string.')

        self.help = help
        self.desc = desc

        self.lexer = lexer or ShlexLexer(set(prefixes), set(triggers + [self.name]))
        self.parser = parser or Parser()

    def _lex(self, msg: Message) -> List[str]:
        return self.lexer.lex(msg)

    def _parse(self, tokens: List[str], handler: Callable) -> List[Any]:
        return self.parser.parse(tokens, handler)

    def prepare(self, msg: Message) -> List[Any]:
        """
        parse msg, prepare arg list from the msg

        :param msg: the msg going to be lexed and parsed
        :return:
        """
        tokens = self._lex(msg)
        args = self._parse(tokens, self.handler)
        return args

    def execute(self, msg: Message, *args):
        """
        pass msg and args from prepare() to handler()

        :param msg:
        :param args: the returned list of prepare()
        :return:
        """
        try:
            self.handler(msg, *args)
        except Exception:
            raise Command.ExecuteException(self.handler)

    def do(self, msg: Message):
        """
        wrapper for prepare() and execute()

        :param msg: what wanna be handled
        """
        self.execute(msg, self.prepare(msg))

    @staticmethod
    def command(name: str, help: str = '', desc: str = '',
                lexer: Lexer = None, prefixes: List[str] = ('/',), triggers: List[str] = (),
                parser: Parser = None):
        """
        decorator, to wrap a func into a Command

        :param name: the name of this Command, also used to trigger
        :param help: detailed manual
        :param desc: short introduction
        :param lexer:
        :param triggers:
        :param parser:
        :param prefixes:
        :return: wrapped Command
        """
        return lambda func: Command(name, func, help, desc, lexer, prefixes, triggers, parser)

    class ExecuteException(Exception):
        def __init__(self, func):
            self.func = func
