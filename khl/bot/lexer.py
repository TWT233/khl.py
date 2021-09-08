import logging
import shlex
from abc import ABC, abstractmethod
from typing import List, Set

from ..message import Message

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
        for prefix in [p for p in self.prefixes if msg.content.startswith(p)]:  # get matched prefix
            # tear down
            try:
                arg_list = shlex.split(msg.content)
            except Exception:
                raise DefaultLexer.MalformedContent(msg)

            # check if trigger exists
            if arg_list[0][len(prefix):] in self.triggers:
                # exists
                return arg_list[1:]  # arg_list[0] is trigger
            else:
                # not exists
                raise DefaultLexer.NoMatchedTrigger(msg)

        # no matched prefix(did not enter the for-loop)
        raise DefaultLexer.NoMatchedPrefix(msg)

    class MalformedContent(Lexer.LexerException):
        pass

    class NoMatchedPrefix(Lexer.LexerException):
        pass

    class NoMatchedTrigger(Lexer.LexerException):
        pass

# TODO: regex lexer
