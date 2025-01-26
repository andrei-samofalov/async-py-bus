import typing as t
from typing import Optional

from pybus.base.handlers import HandlerWrapper
from pybus.base.routers.eventrouter import EventRouter
from pybus.base.routers.requestrouter import RequestRouter
from pybus.core import exceptions as exc
from pybus.core.api.broker import AbstractBrokerAdapter
from pybus.core.api.dispatcher import DispatcherProtocol
from pybus.core.api.typing import HandlerType, MessageType
from pybus.core.types import EMPTY


class Dispatcher(DispatcherProtocol[EventRouter, RequestRouter, HandlerWrapper]):
    """Base dispatcher protocol implementation."""

    def __init__(
        self,
        events_router_cls: type[EventRouter] = EventRouter,
        commands_router_cls: Optional[type[RequestRouter]] = RequestRouter,
        queries_router_cls: Optional[type[RequestRouter]] = None,
        broker: Optional[AbstractBrokerAdapter] = None,
    ) -> None:
        self._events = events_router_cls(self)
        self._commands = commands_router_cls(self) if commands_router_cls is not None else None
        self._queries = queries_router_cls(self) if queries_router_cls is not None else None

        self._broker = broker
        self._started = False

    @property
    def events(self):  # pragma: no cover
        ...

    @events.getter
    def events(self) -> EventRouter:
        """Return events proxy"""
        if self._events is None:
            raise exc.ImproperlyConfigured(
                reason="Dispatcher Commands router has not been initialized"
            )
        return self._events

    @property
    def commands(self):  # pragma: no cover
        ...

    @commands.getter
    def commands(self) -> RequestRouter:
        """Return commands proxy"""
        if self._commands is None:
            raise exc.ImproperlyConfigured(
                reason="Dispatcher Commands router has not been initialized"
            )
        return self._commands

    @property
    def queries(self):  # pragma: no cover
        ...

    @queries.getter
    def queries(self) -> RequestRouter:
        """Return queries proxy"""
        if self._queries is None:
            raise exc.ImproperlyConfigured(
                reason="Dispatcher Queries router has not been initialized"
            )
        return self._queries

    @property
    def is_started(self) -> bool:
        """Return True if dispatcher has started."""
        return self._started

    def register_event_handler(  # noqa
        self,
        message: MessageType,
        handler: HandlerType,
        argname: t.Optional[str] = EMPTY,
        **initkwargs,
    ) -> HandlerWrapper:
        return self.events.bind(message, handler, argname, **initkwargs)

    def register_command_handler(  # noqa
        self,
        message: MessageType,
        handler: HandlerType,
        argname: t.Optional[str] = EMPTY,
        **initkwargs,
    ) -> HandlerWrapper:
        return self.commands.bind(message, handler, argname, **initkwargs)

    def register_query_handler(  # noqa
        self,
        message: MessageType,
        handler: HandlerType,
        argname: t.Optional[str] = EMPTY,
        **initkwargs,
    ) -> HandlerWrapper:
        return self.queries.bind(message, handler, argname, **initkwargs)

    def start(self) -> None:
        """Start the dispatcher."""
        if self._events is None:
            raise exc.ImproperlyConfigured(
                reason=f'{self.__class__.__name__} needs at least event router to work'
            )

        self.events.setup(broker=self._broker, name='events')

        if self._commands:
            self.commands.setup(broker=self._broker, name='commands')

        if self._queries:
            self.queries.setup(broker=self._broker, name='queries')

        self._started = True


default_dispatcher = Dispatcher()
