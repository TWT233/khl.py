import shlex
from typing import Tuple, Iterable, List

from khl.message import TextMsg


def parser(msg: TextMsg, prefixes: Iterable) -> Tuple[TextMsg, List[str]]:
    # msg = TextMsg(**event)
    for prefix in prefixes:
        if msg.content.startswith(prefix):
            raw_cmd = shlex.split(msg.content[len(prefix):])
            raw_cmd[0] = raw_cmd[0].lower()
            return msg, raw_cmd

    return msg, []
