from ._enums import MILLISECONDS as MILLISECONDS, SECONDS as SECONDS, SocketEvt as SocketEvt, Time as Time
from ._exceptions import CurlError as CurlError
from .abc import RequestProtocol as RequestProtocol
from .scalars import Quantity as Quantity
from socket import socket as Socket
from typing import Self, TypeAlias, TypeVar

T = TypeVar('T')
Event: TypeAlias

class Multi:
    def __init__(self) -> None: ...
    async def process(self, request: RequestProtocol[T]) -> T: ...

class _ExternalSocket(Socket):
    def __del__(self) -> None: ...
    @classmethod
    def from_fd(cls, fd: int) -> Self: ...
