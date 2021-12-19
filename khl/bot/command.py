import asyncio
import inspect
import logging
from typing import Callable, Coroutine, List, Union, Pattern, Any, Type

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

    def params(self, ignores: List[Type]) -> (List[Type], List[inspect.Parameter]):
        """get parameters that need to be parsed according to `ignores`

        :param ignores: list of types that need to be filtered

        :return: a tuple: (the filtered params(need to be filled in outer context), the params need to be parsed)
        """
        filtered = []
        params = list(inspect.signature(self.handler).parameters.values())
        for t in ignores:
            if len(params) <= 0:
                break
            if t == params[0].annotation:
                filtered.append(params.pop(0).annotation)
        return filtered, params

    def prepare(self, msg: Message, params: List[inspect.Parameter]) -> List:
        """
        parse msg, prepare arg list from the msg

        :param msg: the msg going to be lex and parsed
        :param params:
        :return:
        """
        tokens = self._lex(msg)
        args = self._parse(tokens, params)
        return args

    def _lex(self, msg: Message) -> List[str]:
        return self.lexer.lex(msg)

    def _parse(self, tokens: List[str], params: List[inspect.Parameter]) -> List:
        return self.parser.parse(tokens, params)

    async def execute(self, msg: Message, *args):
        """
        pass msg and args from prepare() to handler()

        :param msg:
        :param args: the returned list of prepare()
        :return:
        """
        log.info(f'command {self.name} was triggered by msg: {msg.content}')
        if await self._check_rules(msg):
            await self.handler(*args)

    async def _check_rules(self, msg: Message):
        result = True
        # usually, there is only one or two rules, thus we need not check rules concurrently
        for rule in self.rules:
            result = result and await self._wrap_rule(rule, msg)
        return result

    @staticmethod
    async def _wrap_rule(rule, msg: Message) -> bool:
        if asyncio.iscoroutinefunction(rule):
            return bool(await rule(msg))
        else:
            return bool(rule(msg))

    def on_check(self, rule: TypeRule):
        ...

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
