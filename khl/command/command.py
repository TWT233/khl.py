"""component Command"""
import asyncio
import inspect
import logging
from copy import copy
from typing import Callable, Coroutine, List, Union, Pattern, Any, Dict

from khl import Message, Client
from .exception import default_exc_handler, TypeEHandler, Exceptions
from .lexer import Lexer, RELexer, DefaultLexer
from .parser import Parser
from .rule import TypeRule
from .util import wrap_if_coro

log = logging.getLogger(__name__)

TypeHandler = Callable[..., Coroutine]


def _get_arg_by_key_type(annotation, predefined_args: dict):
    for v in predefined_args.values():
        if isinstance(v, annotation):
            return v
    return None


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
    exc_handlers: Dict[Any, TypeEHandler]

    def __init__(
        self,
        name: str,
        handler: TypeHandler,
        help: str,
        desc: str,
        lexer: Lexer,
        parser: Parser,
        rules: List[TypeRule],
        exc_handlers: Dict[Any, TypeEHandler]
    ):
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
        self.exc_handlers = copy(default_exc_handler) if exc_handlers is None else dict(exc_handlers)

    @staticmethod
    def command(
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
        case_sensitive: bool = True
    ) -> Callable[[TypeHandler], 'Command']:
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
        :param case_sensitive: is the command trigger sensitive
        :return: a decorator to wrap Command
        """
        if not lexer and regex:
            lexer = RELexer(regex) if isinstance(regex, str) else regex

        def decorator(handler: TypeHandler):
            default_lexer = DefaultLexer(set(prefixes), set([name or handler.__name__] + list(aliases)), case_sensitive)
            return Command(name, handler, help, desc, lexer or default_lexer, parser or Parser(), rules, exc_handlers)

        return decorator

    def on_exception(self, type=Exception):
        """returns a decorator, register an exception handler to the command

        handler is invoked when exception/subclass exception raised during command handling

        the exception handler signature & usage example::

            @bot.command()
            async def foo(m: Message, i: int, *a: float):
                ...

            @foo.on_exception(Exceptions.Handler.ArgLenNotMatched)
            async def foo_on_arg_len(cmd: Command, exc: Exceptions.Handler.ArgLenNotMatched, msg: Message):
                ...

        note: the param `exc` can be typed according to the type passed to `on_exception`
        """

        def decorator(handler: TypeEHandler):
            self.exc_handlers[type] = handler

        return decorator

    async def handle(self, msg: Message, client: Client, predefined_kwargs: dict):
        """handle msg:

        1. check if matched the command
        2. if matched, execute the command handler"""
        try:
            predefined_args, to_be_parsed = self._split_params(predefined_kwargs)
            parsed_args = await self.parser.parse(msg, client, self.lexer.lex(msg), to_be_parsed)

            log.info(f'command {self.name} is triggered by msg: {msg.content}')

            await self._check_rules(msg)
            self._check_arg_len(to_be_parsed, parsed_args)

            await self.handler(*predefined_args, *parsed_args)
        except Exception as e:
            return await self._handle_exc(e, msg)

    def _split_params(self, predefined_kwargs: dict) -> (List[Any], List[inspect.Parameter]):
        """get parameters that need to be parsed according to `ignores`

        :param predefined_kwargs: list of predefined kwargs

        :return: a tuple: (the used predefined args, the params need to be parsed)
        """
        predefined_args = []
        to_be_parsed = []
        params = list(inspect.signature(self.handler).parameters.values())
        for p in params:
            predefined = _get_arg_by_key_type(p.annotation, predefined_kwargs)
            if predefined is not None:
                predefined_args.append(predefined)
            else:
                to_be_parsed.append(p)
        return predefined_args, to_be_parsed

    async def _check_rules(self, msg: Message):
        """:raise Exceptions.Handler.RuleNotPassed: if there is rule not passed"""
        # usually, there is only one or two rules, thus no need to check rules concurrently
        for rule in self.rules:
            if not bool(await wrap_if_coro(rule(msg))):
                raise Exceptions.Handler.RuleNotPassed(rule)

    @staticmethod
    def _check_arg_len(to_be_parsed: List[inspect.Parameter], parsed_args: List):
        """:raise Exceptions.Handler.ArgLenNotMatched: if parsed_args len not matched to_be_parsed"""

        def is_positional(p):
            return p.kind is inspect.Parameter.VAR_POSITIONAL

        def has_default(p):
            return p.default is not inspect.Parameter.empty

        minn = sum(map(
            lambda p: 1 if not is_positional(p) and not has_default(p) else 0,
            to_be_parsed,
        ))
        maxx = -1 if inspect.Parameter.VAR_POSITIONAL in map(lambda x: x.kind, to_be_parsed) else len(to_be_parsed)
        if len(parsed_args) < minn or (maxx != -1 and len(parsed_args) > maxx):
            raise Exceptions.Handler.ArgLenNotMatched(minn, maxx, len(parsed_args))

    async def _handle_exc(self, e, msg: Message):
        """lookup self.exc_handlers if type(e) exists, execute it"""
        handlers = [self.exc_handlers[h] for h in self.exc_handlers if isinstance(e, h)]
        return await asyncio.gather(*[h(self, e, msg) for h in handlers])
