import asyncio
import logging
from typing import Callable, Coroutine, List, Union, Pattern, Any

from .lexer import Lexer, RELexer, DefaultLexer
from .parser import Parser
from .rule import TypeRule
from ..message import Message

log = logging.getLogger(__name__)

TypeHandler = Callable[..., Coroutine]
TypeEHandler = Callable[[Message, Any, Exception], Coroutine]


class Command:
    """
    Receive a `Message`, parse it with `lex` and `parser`, execute `handler` if successfully parsed else discard it
    """
    name: str
    handler: TypeHandler
    help: str
    desc: str

    lexer: Lexer
    parser: Parser

    rules: List[TypeRule]
    exception_handlers: List[TypeEHandler]

    def __init__(self, name: str, handler: TypeHandler, help: str, desc: str, lexer: Lexer, parser: Parser,
                 rules: List[TypeRule], exception_handlers: List[TypeEHandler]):
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
        self.exception_handlers = list(exception_handlers)

    @staticmethod
    def command(name: str = '', *, help: str = '', desc: str = '',
                aliases: List[str] = (), prefixes: List[str] = ('/',), regex: Union[str, Pattern] = '',
                lexer: Lexer = None, parser: Parser = None,
                rules: List[TypeRule] = (), exception_handlers: List[TypeEHandler] = ()):
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
        :param rules: command executed if all rules are checked
        :param exception_handlers: executed when exception raised
        :return: wrapped Command
        """
        if not lexer and regex:
            lexer = regex if isinstance(regex, Pattern) else RELexer(regex)
        parser = parser or Parser()

        def decorator(handler: TypeHandler):
            default_lexer = DefaultLexer(set(prefixes), set([name or handler.__name__] + list(aliases)))
            return Command(name, handler, help, desc, lexer or default_lexer, parser, rules, exception_handlers)

        return decorator

    def prepare(self, msg: Message) -> List:
        """
        parse msg, prepare arg list from the msg

        :param msg: the msg going to be lexed and parsed
        :return:
        """
        tokens = self._lex(msg)
        args = self._parse(tokens, self.handler)
        return args

    def _lex(self, msg: Message) -> List[str]:
        return self.lexer.lex(msg)

    def _parse(self, tokens: List[str], handler: TypeHandler) -> List:
        return self.parser.parse(tokens, handler)

    async def execute(self, msg: Message, *args):
        """
        pass msg and args from prepare() to handler()

        :param msg:
        :param args: the returned list of prepare()
        :return:
        """
        log.info(f'command {self.name} was triggered by msg: {msg.content}')
        try:
            if await self._check_rules(msg, *args):
                await self.handler(msg, *args)
        except Exception as e:
            log.exception(e)

    async def _check_rules(self, msg: Message, *args):
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

    def on_check(self, rule: TypeRule):
        ...

    def do(self, msg: Message):
        """
        wrapper for prepare() and execute()

        :param msg: what wanna be handled
        """
        self.execute(msg, *self.prepare(msg))

    def on_error(self, exception_handler: TypeEHandler):
        self.exception_handlers.append(exception_handler)

    async def cover_exception(self, msg: Message, bot, e: Exception):
        """
        executed when an exception is raised. If this func raise, there is no fallback
        
        :param msg: the message caused exception
        :param bot: the bot received the msg
        :param e: the exception raised
        """
        await asyncio.gather(*[h(msg, bot, e) for h in self.exception_handlers])
