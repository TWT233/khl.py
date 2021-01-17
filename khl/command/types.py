from enum import Enum
from typing import Any
from khl.command.session import Session


class Result(Enum):
    SUCCESS = 'SUCCESS'
    FAIL = 'FAIL'
    ERROR = 'ERROR'


class CommandType(Enum):
    MENU = 'MENU'
    APP = 'APP'


class FuncResult[T](object):
    result_type: Result
    return_data: T
    msg_sent: Any
    detail: Any
