import asyncio
import copy
import inspect
import logging
from typing import Dict, Any, Callable, List, Coroutine

from .. import User, Channel


log = logging.getLogger(__name__)


def _get_param_type(params: List[inspect.Parameter], index: int):
    # empty param list: str in default
    if len(params) <= 0:
        return str

    # for *args: result = the last param type
    result = params[min(index, len(params) - 1)].annotation

    # no type hint: str in default
    if result == inspect.Parameter.empty:
        result = str
    return result


class Parser:
    """
    deal with a list of tokens made from Lexer, convert their type to match the command.handler
    """
    _parse_funcs: Dict[Any, Callable] = {
        str: lambda token: token,
        int: lambda token: int(token),
        float: lambda token: float(token)
    }

    def __init__(self, **kwargs):
        self._parse_funcs = copy.copy(Parser._parse_funcs)
        self._parse_funcs[User] = self._parse_user
        self._parse_funcs[Channel] = self._parse_channel
        # TODO: Role parser
        self.client = kwargs.get("_client_")

    async def parse(self, tokens: List[str], params: List[inspect.Parameter]) -> List[Any]:
        """
        parse tokens into args that types corresponding to handler's requirement

        :param tokens: output of Lexer.lex()
        :param params: command handlers parameters
        :return: List of args
        :raise: Parser.ArgListLenNotMatch
        """
        ret = []
        for i in range(len(tokens)):
            param_type = _get_param_type(params, i)

            if param_type not in self._parse_funcs:
                raise Parser.ParseFuncNotExists(params[i])

            try:
                call = self._parse_funcs[param_type](tokens[i])
                if isinstance(call, Coroutine):
                    call = await call
                ret.append(call)
            except Exception as e:
                raise Parser.ParseException(e) from e
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

        # insert, remember this is a replacement
        self._parse_funcs[s.return_annotation] = func
        return func

    async def _parse_user(self, token) -> User:
        if not (token.startswith("(met)") and token.startswith("(met)")):
            raise Parser.ParseException(RuntimeError("Failed to parse user"))
        return await self.client.fetch_user(token[5:len(token) - 5])

    async def _parse_channel(self, token) -> Channel:
        if not (token.startswith("(chn)") and token.startswith("(chn)")):
            raise Parser.ParseException(RuntimeError("Failed to parse channel"))
        return await self.client.fetch_public_channel(token[5:len(token) - 5])

    class ParserException(Exception):
        pass

    class TooMuchArgs(ParserException):

        def __init__(self, expected: int, exact: int, func: Callable):
            self.expected = expected
            self.exact = exact
            self.func = func

    class ParseFuncNotExists(ParserException):

        def __init__(self, expected: inspect.Parameter):
            self.expected = expected

    class ParseException(ParserException):

        def __init__(self, err: Exception):
            self.err = err
