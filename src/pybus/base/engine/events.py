from pybus.base.maps import EventHandlerMap
from pybus.core.api.engine import AbstractEngine
from pybus.core.api.typing import MessageType, PyBusWrappedHandler


class EventEngine(AbstractEngine[EventHandlerMap]):

    async def handle(self, handlers: frozenset[PyBusWrappedHandler], message: MessageType):
        new_events = []
        for handler in handlers:
            await handler.handle(message)
            new_events.extend(await handler.dump_events())

        return new_events

    async def handle_side_events(self, *events: MessageType) -> None:
        """Handle side handler event"""
        for event in events:
            await self.put_to_queue(event)
