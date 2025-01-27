import abc
from abc import ABC
from typing import Self

from pybus.core.api.handlers import AbstractHandler
from pybus.core.api.typing import MessageType


class HandlerMeta(abc.ABCMeta):
    """Abstract Handler Meta"""

    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        obj._events = []
        return obj

    def __new__(mcs, name: str, bases: tuple, namespace: dict, /, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        # cls._events = []
        cls.dump_events = mcs._dump_events
        cls.add_event = mcs._add_event

        return cls

    async def _dump_events(self: Self) -> list[MessageType]:
        events = self._events
        self._events = []
        return events

    async def _add_event(self: Self, event: MessageType) -> None:
        self._events.append(event)


class PyBusAbstractHandler(AbstractHandler, ABC, metaclass=HandlerMeta):
    """
    PyBusHandler abstract base class.

    To implement:
      - handle

    """
