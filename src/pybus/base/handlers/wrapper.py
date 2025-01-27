import functools
import inspect
from logging import getLogger

from pybus.core import helpers
from pybus.core.api.handlers import AbstractHandlerWrapper
from pybus.core.api.typing import MessageType
from pybus.core.types import EMPTY

logger = getLogger(__name__)


class HandlerWrapper(AbstractHandlerWrapper):
    """Handler wrapper."""

    def __repr__(self):
        return helpers.handler_repr(self._handler)

    __str__ = __repr__

    async def handle(self, message: MessageType):
        """Handle message."""
        fn = self._handler.handle if hasattr(self._handler, 'handle') else self._handler
        handler = functools.partial(fn, **self._initkwargs)

        if not self._inject:
            result = await handler()
        elif self._argname is not EMPTY:
            result = await handler(**{self._argname: message})
        else:
            result = await handler(message)

        if result and not hasattr(self._handler, 'add_event'):
            await self.add_event(result)

        return result

    async def can_handle(self, message: MessageType) -> bool:
        """Return True if handler can handle the given message."""
        if hasattr(self._handler, 'can_handle'):
            return await self._handler.can_handle(message)

        ret = self._message is not EMPTY and (
            message == self._message
            or (
                inspect.isclass(self._message)
                and (isinstance(message, self._message) or issubclass(message, self._message))
            )
        )

        return ret

    async def add_event(self, event: MessageType):
        """Add event to emit later."""
        if hasattr(self._handler, 'add_event'):
            return await self._handler.add_event(event)

        self._events.append(event)

    async def dump_events(self):
        """Return list of collected events."""
        if hasattr(self._handler, 'dump_events'):
            return await self._handler.dump_events()

        events = self._events
        self._events = []
        return events
