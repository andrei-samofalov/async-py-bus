import abc
import typing as t

from pybus.base.handlers.wrapper import HandlerWrapper
from pybus.core.api.routers import AbstractMessageRouter
from pybus.core.api.typing import EngineType, HandlerType, MessageType
from pybus.core.inspection import sig


class AbstractBaseMessageRouter(
    AbstractMessageRouter[EngineType, HandlerWrapper],
    t.Generic[EngineType],
    metaclass=abc.ABCMeta
):
    """Base class for event and request router implementations."""

    def get_meta(
        self,
        message: MessageType,
        handler: HandlerType,
        argname: t.Optional[str],
        **initkwargs,
    ) -> sig.HandlerMetaData:
        """Return Handler meta"""
        return sig.check_signature(handler, message, argname, **initkwargs)
