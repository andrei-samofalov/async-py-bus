import typing as t

from pybus.core.api.typing import (
    EventRouterType,
    HandlerType,
    MessageType,
    PyBusWrappedHandler,
    RequestRouterType,
)
from pybus.core.types import EMPTY


@t.runtime_checkable
class DispatcherProtocol(t.Protocol[EventRouterType, RequestRouterType, PyBusWrappedHandler]):
    """DispatcherProtocol protocol."""

    @property
    def events(self) -> EventRouterType:
        """Return events proxy"""

    @property
    def commands(self) -> RequestRouterType:
        """Return commands proxy"""

    @property
    def queries(self) -> RequestRouterType:
        """Return queries proxy"""

    @property
    def is_started(self) -> bool:
        """Return True if dispatcher has started."""

    def register_event_handler(
        self,
        message: MessageType,
        handler: HandlerType,
        argname: t.Optional[str] = EMPTY,
        **initkwargs,
    ) -> PyBusWrappedHandler:
        """Register event handler."""

    def register_command_handler(
        self,
        message: MessageType,
        handler: HandlerType,
        argname: t.Optional[str] = EMPTY,
        **initkwargs,
    ) -> PyBusWrappedHandler:
        """Register command handler."""

    def register_query_handler(
        self,
        message: MessageType,
        handler: HandlerType,
        argname: t.Optional[str] = EMPTY,
        **initkwargs,
    ) -> PyBusWrappedHandler:
        """Register query handler."""
