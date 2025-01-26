from pybus.base.engine.events import EventEngine
from pybus.base.maps import RequestHandlerMap
from pybus.core.api.engine import AbstractEngine
from pybus.core.api.typing import MessageType, PyBusWrappedHandler


class RequestEngine(AbstractEngine[RequestHandlerMap]):

    def __init__(self, event_engine: EventEngine, message_map: RequestHandlerMap):
        super().__init__(message_map=message_map)
        self._event_engine = event_engine

    async def handle(self, handler: PyBusWrappedHandler, message: MessageType):
        await handler.handle(message)
        return await handler.dump_events()

    async def handle_side_events(self, *events: MessageType) -> None:
        """Handle side handler event"""
        for event in events:
            await self._event_engine.put_to_queue(event)
