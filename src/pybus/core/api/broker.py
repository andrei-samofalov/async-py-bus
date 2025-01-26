import abc

from pybus.core.api.typing import MessageType


class AbstractBrokerAdapter(metaclass=abc.ABCMeta):
    """Broker adapter."""

    @abc.abstractmethod
    def get_workers(self) -> int:
        """Get number of workers."""

    @abc.abstractmethod
    async def get(self) -> MessageType:
        """Get message from the broker queue."""
