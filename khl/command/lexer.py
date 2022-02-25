import logging
import re
import shlex
from abc import ABC, abstractmethod
from typing import List, Set, Union, Pattern

from khl.message import Message

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

    class LexerException(Exception):

        def __init__(self, msg: Message):
            self.msg = msg

    class NotMatched(LexerException):
        ...


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
            raise Lexer.NotMatched(msg)

        for prefix in matched_prefixes:
            try:
                arg_list = shlex.split(msg.content)
            except Exception:
                raise DefaultLexer.MalformedContent(msg)
            # check if trigger exists
            if arg_list[0][len(prefix):] not in self.triggers:
                raise Lexer.NotMatched(msg)
            return arg_list[1:]  # arg_list[0] is trigger

    class MalformedContent(Lexer.LexerException):
        pass

    class NoMatchedTrigger(Lexer.LexerException):
        pass


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
            raise Lexer.NotMatched(msg)
        return [m[i] for i in range(1, len(m.groups()) + 1) if m.start(i) < len(msg.content)]
