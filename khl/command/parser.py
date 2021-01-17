from typing import Mapping
from khl.command.base import BaseCommand


def parser(content: str, prefix: str, commandMap: Mapping[str,
                                                          BaseCommand]) -> str:
    return ''
