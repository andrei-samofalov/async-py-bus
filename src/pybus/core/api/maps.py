import abc
import copy
import inspect
from types import MappingProxyType
from typing import Generic

from pybus.core.api.handlers import AbstractHandlerWrapper
from pybus.core.api.typing import (
    HandlerType,
    MapReturnType,
    MessageType,
    PyBusHandlerMeta,
    PyBusWrappedHandler,
)


class AbstractHandlerMap(Generic[MapReturnType], metaclass=abc.ABCMeta):
    """Handler map.

    Abstract methods:
      - add
      - find
      - freeze
      - wrap_handler
    """

    def __init__(self):
        self._storage = {}
        self._frozen = False

    @property
    def frozen(self):
        """Return frozen state"""
        return self._frozen

    @classmethod
    def make_key(cls, message: MessageType) -> MessageType:
        """Return message key"""
        m_type = message if inspect.isclass(message) else type(message)
        return m_type if not issubclass(m_type, str) else message

    def build(self):
        """Build map. Handlers would be frozen after."""
        if self._frozen:
            raise RuntimeError("map is frozen")

        map_keys = list(self._storage.keys())
        map_copy = copy.copy(self._storage)
        self._storage.clear()

        for m_key in map_keys:
            self._storage[m_key] = self.freeze(map_copy[m_key])

        self._storage = MappingProxyType(self._storage)
        self._frozen = True

    def can_handle(self, message: MessageType) -> bool:
        """Return True if the given message key can be handled."""
        return self.make_key(message) in self._storage

    @abc.abstractmethod
    def add(self, message: MessageType, handler: PyBusWrappedHandler) -> None:
        """Add handler to the map."""

    @abc.abstractmethod
    def find(self, key: MessageType) -> MapReturnType:
        """Return handler or handlers for the given key."""

    @abc.abstractmethod
    def wrap_handler(self, meta: PyBusHandlerMeta) -> AbstractHandlerWrapper:
        """Wrap handler"""

    @classmethod
    @abc.abstractmethod
    def freeze(cls, val: HandlerType | set[HandlerType]) -> MapReturnType:
        """Freeze map value."""
