"""parser: component used in command args handling, convert string token to fit the command signature"""
import asyncio
import copy
import inspect
import logging
from typing import Dict, Any, Callable, List, Union

from khl import User, Channel, Client, Message, Role
from .exception import Exceptions
from .util import wrap_if_coro

log = logging.getLogger(__name__)


def _get_param(params: List[inspect.Parameter], index: int) -> Union[inspect.Parameter, None]:
    if len(params) <= 0:
        return None
    # for *args: result = the last param
    return params[min(index, len(params) - 1)]


def _get_param_type(param: Union[inspect.Parameter, None]):
    # str in default
    if param is None:
        return str
    if param.annotation == inspect.Parameter.empty:  # no type hint: str in default
        return str
    return param.annotation


async def _parse_user(_, client, token) -> User:
    if not (token.startswith("(met)") and token.endswith("(met)")):
        raise ValueError(f"wrong format: expected: '(met)`user_id`(met)', actual: {token}")
    return await client.fetch_user(token[5:-5])


async def _parse_channel(_, client, token) -> Channel:
    if not (token.startswith("(chn)") and token.endswith("(chn)")):
        raise ValueError(f"wrong format: expected: '(chn)`channel_id`(chn)', actual: {token}")
    return await client.fetch_public_channel(token[5:-5])


async def _parse_role(msg, _, token) -> Role:
    if not (token.startswith("(rol)") and token.endswith("(rol)")):
        raise ValueError(f"wrong format: expected: '(rol)`role_id`(rol)', actual: {token}")
    role_id = int(token[5:-5])
    role = next(filter(lambda r: r.id == role_id, await msg.ctx.guild.fetch_roles()), None)
    if role is None:
        raise ValueError("role not found in the guild")
    return role


class Parser:
    """
    deal with a list of tokens made from Lexer, convert their type to match the command.handler
    """
    _parse_funcs: Dict[Any, Callable] = {
        str: lambda msg, client, token: token,
        int: lambda msg, client, token: int(token),
        float: lambda msg, client, token: float(token),
        User: _parse_user,
        Channel: _parse_channel,
        Role: _parse_role
    }

    def __init__(self):
        self._parse_funcs = copy.copy(Parser._parse_funcs)

    async def parse(
        self,
        msg: Message,
        client: Client,
        tokens: List[str],
        params: List[inspect.Parameter],
    ) -> List[Any]:
        """
        parse tokens into args that types corresponding to handler's requirement

        :param msg: message object
        :param client: bot client
        :param tokens: output of Lexer.lex()
        :param params: command handlers parameters
        :return: List of args
        :raise: Parser.ArgListLenNotMatch
        """
        ret = []
        for i, token in enumerate(tokens):
            param = _get_param(params, i)
            param_type = _get_param_type(param)

            if param_type not in self._parse_funcs:
                raise Exceptions.Parser.NoParseFunc(param, token)
            func = self._parse_funcs[param_type]

            try:
                arg = await wrap_if_coro(func(msg, client, token))
            except Exception as e:
                raise Exceptions.Parser.ParseFailed(param, token, func, e)

            ret.append(arg)
        return ret

    def register(self, func):
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
