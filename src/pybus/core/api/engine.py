import abc
import asyncio
from logging import getLogger
from typing import Generic, Optional

from pybus.core.api.broker import AbstractBrokerAdapter
from pybus.core.api.typing import MapReturnType, MessageMapType, MessageType

logger = getLogger(__name__)


class AbstractEngine(Generic[MessageMapType], metaclass=abc.ABCMeta):
    """Engine protocol.

    Implement:
      - handle
    """

    def __init__(self, message_map: MessageMapType):
        self._map = message_map
        self._queue = asyncio.Queue()
        self._broker: Optional[AbstractBrokerAdapter] = None
        self._workers: int = 0
        self._name: Optional[str] = None

        self._started = False

    @property
    def is_started(self) -> bool:
        """Return True if the engine is started."""
        return self._started

    def set_name(self, name: str):
        """Set the engine name."""
        self._name = name or self.__class__.__name__

    async def put_to_queue(self, message: MessageType) -> None:
        """Send message"""
        await self._queue.put(message)

    async def _worker(self):
        self._workers += 1
        worker = f"{self._name!r} worker #{self._workers}"
        logger.debug(f"{worker} started.")

        while True:
            try:
                logger.debug(f'{worker} waiting for messages...')
                message = await self._queue.get()
                logger.debug(f'{worker} got message: {message!r}')

                handler = self._map.find(message)

                if new_events := await self.handle(handler, message):
                    logger.debug(f'{worker} got new events: {new_events} from {handler!r}')
                    await self.handle_side_events(*new_events)

                else:
                    logger.debug(f'{worker} no new events from {handler!r}')

            except asyncio.CancelledError:
                break

            except Exception as e:
                await self.handler_error(e)

    async def _broker_loop(self) -> None:
        while True:
            try:
                message = await self._broker.get()
                await self.put_to_queue(message)
            except asyncio.CancelledError:
                break

    async def handler_error(self, error: str | Exception) -> None:  # noqa
        """Error handler"""
        logger.exception(error)

    @abc.abstractmethod
    async def handle(self, handler: MapReturnType, message: MessageType) -> list[MessageType]:
        """Handler the message. Optionally can return new messages."""

    @abc.abstractmethod
    async def handle_side_events(self, *events: MessageType) -> None:
        """Handle handler event"""

    def setup_broker(self, broker: AbstractBrokerAdapter):
        """Setup broker loop."""
        if broker is None:
            return logger.error('broker was not provided')

        self._broker = broker
        tasks = [self._broker_loop() for _ in range(broker.get_workers())]
        asyncio.gather(*tasks)

        # additional workers for broker queue
        self.start(workers=broker.get_workers())

    def start(self, workers: int = 3) -> None:
        """Start the engine."""
        tasks = [self._worker() for _ in range(workers)]
        asyncio.gather(*tasks)

        self._started = True
