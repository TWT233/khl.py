import shlex
from khl.Message import TextMsg
from typing import List, Mapping, Sequence, Tuple, Union
from .base import BaseCommand


def parser(
    d: dict, prefixes: Union[List[str], str,
                             tuple], commandMap: Mapping[str, BaseCommand]
) -> Union[Tuple[str, Sequence[str], TextMsg], TextMsg]:
    msg = TextMsg(channel_type=d['channel_type'],
                  target_id=d['target_id'],
                  author_id=d['author_id'],
                  content=d['content'],
                  msg_id=d['msg_id'],
                  msg_timestamp=d['msg_timestamp'],
                  nonce=d['nonce'],
                  extra=d['extra'])

    for prefix in prefixes:
        if msg.content.startswith(prefix):
            res = shlex.split(msg.content[1:])
            command = res[0]
            args = res[1:]
            return (command, args, msg)

    return msg
