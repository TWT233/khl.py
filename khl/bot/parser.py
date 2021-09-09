import asyncio
import copy
import inspect
import logging
from typing import Dict, Any, Callable, List, Tuple

log = logging.getLogger(__name__)


class Parser:
    """
    deal with a list of tokens made from Lexer, convert their type to match the command.handler
    """
    _parse_funcs: Dict[Any, Callable] = {
        str: lambda token: token,
        int: lambda token: int(token),
        float: lambda token: float(token)
        # TODO: tag -> User/Channel/Role...
    }

    def __init__(self):
        self._parse_funcs = copy.copy(Parser._parse_funcs)

    def parse(self, tokens: List[str], handler: Callable) -> List[Any]:
        """
        parse tokens into args that types corresponding to handler's requirement

        :param tokens: output of Lexer.lex()
        :param handler: parse target
        :return: List of args
        :raise: Parser.ArgListLenNotMatch
        """
        s = inspect.signature(handler)
        params = list(s.parameters.items())[1:]  # the first param is `msg: Message`

        # check
        if len(tokens) > len(params):
            raise Parser.TooMuchArgs(len(params), len(tokens), handler)

        # parse
        ret = []
        for i in range(len(tokens)):
            t = params[i][1].annotation  # arg type

            # no type hint for t
            if t == inspect.Parameter.empty:
                ret.append(tokens[i])
                continue

            if t not in self._parse_funcs:
                raise Parser.ParseFuncNotExists(params[i], handler)
            try:
                ret.append(self._parse_funcs[t](tokens[i]))
            except Exception as e:
                raise Parser.ParseFuncException(e)
        return ret

    def register(self, func):  # TODO: global register
        """
        decorator, register the func into object restricted _parse_funcs()

        checks if parse func for that type exists, and insert if not
        :param func: parse func
        """
        s = inspect.signature(func)

        # check: 1. not coroutine, 2. len matches
        if asyncio.iscoroutinefunction(func):
            raise TypeError('parse function should not be async')
        if len(s.parameters) != 1 or list(s.parameters.values())[0].annotation != str:
            raise TypeError('parse function should own only one param, and the param type is str')

        # insert, remember this is a replace
        self._parse_funcs[s.return_annotation] = func
        return func

    class ParserException(Exception):
        pass

    class TooMuchArgs(ParserException):
        def __init__(self, expected: int, exact: int, func: Callable):
            self.expected = expected
            self.exact = exact
            self.func = func

    class ParseFuncNotExists(ParserException):
        def __init__(self, expected: Tuple[str, inspect.Parameter], func: Callable):
            self.expected = expected
            self.func = func

    class ParseFuncException(ParserException):
        def __init__(self, err: Exception):
            self.err = err
