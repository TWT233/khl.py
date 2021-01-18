from .types import ResultType
from typing import Any, Coroutine, Optional
from aiohttp.client_reqrep import ClientResponse


class SessionResult(object):
    result_type: ResultType
    session: Any
    msg_sent: Optional[Coroutine[Any, Any, Any]]
    detail: Any

    def __init__(self,
                 result_type: ResultType,
                 session: Any,
                 msg_sent: Optional[Coroutine[Any, Any, ClientResponse]],
                 detail: Any = None) -> None:
        self.result_type = result_type
        self.session = session
        self.msg_sent = msg_sent
        self.detail = detail