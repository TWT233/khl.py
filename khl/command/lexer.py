import logging
import re
import shlex
from abc import ABC, abstractmethod
from typing import List, Set, Union, Pattern

from khl import Message
from .exception import Exceptions

log = logging.getLogger(__name__)


class Lexer(ABC):
    """
    deal with msg, convert msg.content -> a list of tokens(like tokens in compiler)
    """

    @abstractmethod
    def lex(self, msg: Message) -> List[str]:
        """
        read msg, and get a list of tokens as List[str] for following parser.parse()

        :param msg: which will be torn down into List[str]
        :return: Tuple(is the msg match the lexer, thrived tokens)
        """
        raise NotImplementedError


class DefaultLexer(Lexer):
    """
    lex with python standard module ``shlex``
    """
    prefixes: Set[str]
    triggers: Set[str]

    def __init__(self, prefixes: Set[str], triggers: Set[str]):
        self.prefixes = prefixes
        self.triggers = triggers

    def lex(self, msg: Message) -> List[str]:
        """
        checks if msg starts with any prefix, shlex.split() if hit, then check if starts with any trigger

        :param msg: which will be torn down into List[str]
        :return: Tuple(is the msg match the lexer, thrived tokens)
        :raises:    ShlexLexer.MalformedContent if shlex.split() failed
                    ShlexLexer.NoMatchedPrefix  literally
                    ShlexLexer.NoMatchedTrigger literally
        """
        matched_prefixes = [p for p in self.prefixes if msg.content.startswith(p)]
        if not matched_prefixes:
            raise Exceptions.Lexer.NotMatched()

        for prefix in matched_prefixes:
            try:
                arg_list = shlex.split(msg.content[len(prefix):])
            except Exception as e:
                raise DefaultLexer.MalformedContent(msg) from e
            # check if trigger exists
            if (arg_list[0] if len(arg_list) > 0 else '') not in self.triggers:
                raise Exceptions.Lexer.NotMatched()
            return arg_list[1:]  # arg_list[0] is trigger

    class MalformedContent(Exceptions.Lexer.LexFailed):
        """the content can not be shlex.split()"""


class RELexer(Lexer):
    """
    lex with python built-in module ``re``
    """
    pattern: Pattern

    def __init__(self, regex: Union[str, Pattern]):
        if isinstance(regex, str):
            self.pattern = re.compile(regex)
        else:
            self.pattern = regex

    def lex(self, msg: Message) -> List[str]:
        m = self.pattern.fullmatch(msg.content)
        if not m:
            raise Exceptions.Lexer.NotMatched()
        return [m[i] for i in range(1, len(m.groups()) + 1) if m.start(i) < len(msg.content)]
