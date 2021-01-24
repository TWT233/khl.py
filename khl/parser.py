import shlex
from typing import Tuple, Iterable, List

from khl.message import TextMsg


def parser(d: dict, prefixes: Iterable) -> Tuple[TextMsg, List[str]]:
    msg = TextMsg(**d)

    for prefix in prefixes:
        if msg.content.startswith(prefix):
            raw_cmd = shlex.split(msg.content[len(prefix):])
            return msg, raw_cmd

    return msg, []
