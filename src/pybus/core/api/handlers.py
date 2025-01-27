import abc
import typing as t

from pybus.core.api.typing import HandlerType, MessageType, ReturnType
from pybus.core.types import EMPTY


@t.runtime_checkable
class HandlerProtocol(t.Protocol):
    """Handler protocol for runtime checking."""

    async def handle(self, message: MessageType) -> ReturnType:
        """Handle message."""

    async def add_event(self, event: MessageType) -> None:
        """Add event to emit later."""

    async def dump_events(self) -> list[MessageType]:
        """Return list of collected events."""


class AbstractHandler(t.Generic[ReturnType], metaclass=abc.ABCMeta):
    """Handler protocol."""

    @abc.abstractmethod
    async def handle(self, message: MessageType) -> ReturnType:
        """Handle message."""

    @abc.abstractmethod
    async def add_event(self, event: MessageType) -> None:
        """Add event to emit later."""

    @abc.abstractmethod
    async def dump_events(self) -> list[MessageType]:
        """Return list of collected events."""


class AbstractHandlerWrapper(
    AbstractHandler[ReturnType],
    t.Generic[ReturnType],
    metaclass=abc.ABCMeta,
):
    """Handler wrapper."""

    def __init__(
        self,
        meta: "HandlerMetaDataProtocol",
        **initkwargs,
    ):
        self._handler = meta.handler
        self._message = meta.message
        self._inject = meta.inject
        self._argname = meta.argname

        self._initkwargs = initkwargs
        self._initkwargs.update(meta.initkwargs)
        self._events = []


class HandlerMetaDataProtocol(t.Protocol):
    """Meta data for dispatcher"""
    handler: HandlerType
    inject: bool
    initkwargs: dict = {}
    argname: t.Optional[str] = EMPTY
    message: t.Optional[MessageType] = EMPTY
