import abc
import functools
import typing as t
from collections.abc import Callable
from typing import Optional

from pybus.core.api.broker import AbstractBrokerAdapter
from pybus.core.api.dispatcher import DispatcherProtocol
from pybus.core.api.handlers import HandlerMetaDataProtocol
from pybus.core.api.maps import AbstractHandlerMap
from pybus.core.api.typing import (
    EngineType,
    HandlerType,
    MessageType,
    PyBusWrappedHandler,
)
from pybus.core.types import EMPTY


class AbstractMessageRouter(
    t.Generic[EngineType, PyBusWrappedHandler],
    metaclass=abc.ABCMeta,
):
    """Router protocol."""
    map_cls: type[AbstractHandlerMap]
    engine_cls: type[EngineType]

    def __init__(self, dispatcher: DispatcherProtocol):
        self._dispatcher = dispatcher
        self._map = self.get_map()
        self._engine: Optional[EngineType] = None

    async def send(self, message: MessageType) -> None:
        """Send message to the bus."""
        assert self._dispatcher.is_started, "you should start the dispatcher first"
        assert self._engine.is_started, "you should start the engine first"
        await self._engine.put_to_queue(message)

    @property
    def engine(self) -> EngineType:
        """Return the engine for this router."""
        return self._engine

    def get_map(self):
        """Returns the message handler map."""
        if self.map_cls is None:
            raise NotImplementedError()

        return self.map_cls()

    def bind(
        self,
        message: MessageType,
        handler: HandlerType,
        argname: t.Optional[str] = EMPTY,
        **initkwargs,
    ) -> PyBusWrappedHandler:
        """Bind handler for the given message."""
        meta = self.get_meta(message, handler, argname, **initkwargs)
        return self._map.wrap_handler(meta)

    def register(
        self,
        message: MessageType,
        argname: t.Optional[str] = EMPTY,
        **initkwargs,
    ) -> Callable:
        """Register handler for the given message as decorator."""

        def _wrapper(handler: HandlerType):
            wrapped_handler = self.bind(message, handler, argname, **initkwargs)

            @functools.wraps(handler)
            async def _decorated(*args, **kwargs):
                return await wrapped_handler.handle(*args, **kwargs)

            return _decorated

        return _wrapper

    @abc.abstractmethod
    def get_meta(
        self,
        message: MessageType,
        handler: HandlerType,
        argname: t.Optional[str],
        **initkwargs,
    ) -> HandlerMetaDataProtocol:
        """Return Handler meta"""

    @abc.abstractmethod
    def get_engine(self):
        """Set up the engine for this router."""

    def setup(self, name: Optional[str] = None, broker: Optional[AbstractBrokerAdapter] = None):
        """setup map, routes, ..."""
        self._map.build()

        self._engine = self.get_engine()
        self._engine.set_name(name)
        self._engine.setup_broker(broker=broker)

        self._engine.start()
