import shlex
from khl.message import TextMsg
from typing import List, Mapping, Sequence, Tuple, Union
from .typings import BaseCommand


def parser(
    d: dict, prefixes: Union[List[str], str,
                             tuple], commandMap: Mapping[str, BaseCommand]
) -> Union[Tuple[str, Sequence[str], TextMsg], TextMsg]:
    msg = TextMsg(**d)

    for prefix in prefixes:
        if msg.content.startswith(prefix):
            res = shlex.split(msg.content[1:])
            command = res[0]
            args = res[1:]
            return command, args, msg

    return msg
