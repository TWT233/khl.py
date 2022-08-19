import inspect
import logging
from typing import Any, Dict, Callable, Coroutine

from khl import Message

log = logging.getLogger(__name__)

TypeEHandler = Callable[['Command', Exception, Message], Coroutine]


class Exceptions:
    """built-in exceptions raised from command process procedure"""

    class Lexer:
        """built-in exceptions raised from lexer"""

        class Base(Exception):
            """base of all kinds of exceptions raised from lexer"""

        class NotMatched(Base):
            """the msg content is not matched to the command"""

        class LexFailed(Base):
            """exception raised during lex process"""

            def __init__(self, exc, *args):
                """
                :param exc: original exception raised from lexer
                """
                self.exc = exc
                super().__init__(*args)

    class Parser:
        """built-in exceptions raised from parser"""

        class Base(Exception):
            """base of all kinds of exceptions raised from parser"""

        class NoParseFunc(Base):
            """there is no parse function for expected_type"""

            def __init__(self, expected_param: inspect.Parameter, token: str, *args):
                """
                :param expected_param: expected param info
                :param token: given token
                """
                self.expected_param = expected_param
                self.token_value = token
                super().__init__(*args)

        class ParseFailed(Base):
            """exception raised during token parser function execution"""

            def __init__(self, expected_param: inspect.Parameter, token: str, parse_func, exc, *args):
                """
                :param expected_param: expected param info
                :param token: given token
                :param parse_func: parse function used to parse the token
                :param exc: original exception raised by parse_func
                """
                self.expected_param = expected_param
                self.token = token
                self.parse_func = parse_func
                self.exc = exc
                super().__init__(*args)

    class Handler:
        """built-in exceptions raised during command handling"""

        class Base(Exception):
            """base of all kinds of exceptions raised during command handling"""

        class RuleNotPassed(Base):
            """rules associated with the command not passed"""

            def __init__(self, rule, *args):
                self.rule = rule
                super().__init__(*args)

        class ArgLenNotMatched(Base):
            """arg list length is not matched, too many args/not enough args"""

            def __init__(self, expected_min: int, expected_max: int, actual: int, *args):
                """

                :param expected_min: min expected arg nums
                :param expected_max: max expected arg nums
                :param actual: actual given arg nums
                """
                self.expected_min = expected_min
                self.expected_max = expected_max
                self.actual = actual
                super().__init__(*args)


async def log_on_exc(cmd, e, _):
    """basically log the exception"""
    if isinstance(e, Exceptions.Lexer.NotMatched):  # ignore NotMatched since it is kinda noisy
        return
    log.debug(f'exception raised when handling command: {cmd.name}', exc_info=e)


async def ignore_exc(*_):
    """explicitly ignore the exception"""
    return


default_exc_handler: Dict[Any, TypeEHandler] = {
    Exception: log_on_exc,  # log in default
}
