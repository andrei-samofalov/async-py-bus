import typing as t
from logging import getLogger
from typing import Optional

from pybus.base.handlers.wrapper import HandlerWrapper
from pybus.base.routers.eventrouter import EventRouter
from pybus.base.routers.requestrouter import RequestRouter
from pybus.core import signals
from pybus.core.api.broker import AbstractBrokerAdapter
from pybus.core.api.dispatcher import DispatcherProtocol
from pybus.core.api.typing import HandlerType, MessageType
from pybus.core.types import EMPTY

logger = getLogger('pybus.dispatcher')


class Dispatcher(DispatcherProtocol[EventRouter, RequestRouter, HandlerWrapper]):
    """Base dispatcher protocol implementation."""

    def __init__(
        self,
        events_router_cls: type[EventRouter] = EventRouter,
        commands_router_cls: Optional[type[RequestRouter]] = RequestRouter,
        queries_router_cls: Optional[type[RequestRouter]] = None,
        broker: Optional[AbstractBrokerAdapter] = None,
        listen_for_signals: bool = True,
    ) -> None:
        self._events = events_router_cls(self)
        self._commands = commands_router_cls(self) if commands_router_cls is not None else None
        self._queries = queries_router_cls(self) if queries_router_cls is not None else None

        self._broker = broker
        self._listen_for_signals = listen_for_signals
        self._started = False

    @property
    def events(self):  # pragma: no cover
        return self._events

    @events.getter
    def _(self) -> EventRouter:
        """Return events proxy"""
        if self._events is None:
            logger.info('attaching default event router')
            self._events = EventRouter(self)

        return self._events

    @property
    def commands(self):
        if self._commands is None:
            logger.info('attaching default command router')
            self._commands = RequestRouter(self)

        return self._commands

    @property
    def queries(self):  # pragma: no cover
        if self._queries is None:
            logger.info('attaching default query router')
            self._queries = RequestRouter(self)

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

        if not any([
            self.events is not None,
            self.queries is not None,
            self.commands is not None
        ]):
            return logger.warning('no handlers registered')

        if self._events is not None:
            self.events.setup(broker=self._broker, name='events')

        if self._commands is not None:
            self.commands.setup(broker=self._broker, name='commands')

        if self._queries is not None:
            self.queries.setup(broker=self._broker, name='queries')

        if self._listen_for_signals:
            signals.setup()

        logger.debug(f'{self.__class__.__name__} started.')
        self._started = True


default_dispatcher = Dispatcher()
