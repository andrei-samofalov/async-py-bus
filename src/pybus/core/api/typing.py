import typing as t

if t.TYPE_CHECKING:
    from pybus.core.api.engine import AbstractEngine  # noqa
    from pybus.core.api.handlers import (  # noqa
        AbstractHandler,
        AbstractHandlerWrapper,
        HandlerMetaDataProtocol,
    )
    from pybus.core.api.maps import AbstractHandlerMap  # noqa
    from pybus.core.api.routers import AbstractMessageRouter  # noqa

Message: t.TypeAlias = type[t.Any] | t.Hashable
MessageType = t.TypeVar("MessageType", bound=Message)

P = t.ParamSpec("P")
PyBusHandler = t.TypeVar("PyBusHandler", bound="AbstractHandler")
PyBusWrappedHandler = t.TypeVar("PyBusWrappedHandler", bound="AbstractHandlerWrapper")

PyBusHandlerMeta = t.TypeVar("PyBusHandlerMeta", bound="HandlerMetaDataProtocol")

ReturnType = t.TypeVar("ReturnType", t.Any, None)
HandlerReturnType: t.TypeAlias = t.Awaitable[ReturnType]

HandlerType: t.TypeAlias = t.Union[
    PyBusHandler,
    PyBusWrappedHandler,
    t.Callable[[], HandlerReturnType],
    t.Callable[[MessageType], HandlerReturnType],
    t.Callable[[MessageType, P.kwargs], HandlerReturnType],
]

MessageMapType = t.TypeVar("MessageMapType", bound="AbstractHandlerMap")
MapReturnType = t.TypeVar("MapReturnType", HandlerType, frozenset[HandlerType])

EngineType = t.TypeVar("EngineType", bound="AbstractEngine")

EventRouterType = t.TypeVar('EventRouterType', bound="AbstractMessageRouter")
RequestRouterType = t.TypeVar('RequestRouterType', bound="AbstractMessageRouter")
