import inspect
from typing import Any

from pybus.core.dependency.providers import Provider
from pybus.core.types import ProtocolType

isfun = inspect.isfunction
iscoro = inspect.iscoroutinefunction
getsig = inspect.signature


def has_self(func):
    """Return True if the given function has self attribute."""
    spec = inspect.getfullargspec(func)
    maybehas = len(spec) > 1 and spec[0] in ["cls", 'self']
    return maybehas or inspect.ismethod(func) and not isinstance(func, staticmethod)


def implements_protocol(cls: Any, protocol: ProtocolType):
    """Return True if the given object implements the protocol."""
    if not isinstance(cls, protocol):
        return False

    for name, member in inspect.getmembers(protocol):
        if name.startswith("__"):
            continue

        protocol_member = getattr(protocol, name)
        if not (isfun(protocol_member) or isfun(protocol_member)):
            continue

        class_member = getattr(cls, name, None)
        if iscoro(protocol_member) != iscoro(class_member):
            return False

        if getsig(protocol_member) != getsig(class_member):
            return False

    return True


def unpack_initkwargs(**initkwargs):
    """Resolves dependency injections in initkwargs."""
    result = {}
    for name, value in initkwargs.items():
        if inspect.isclass(value) and issubclass(value, Provider):
            value = value.call(name)

        result[name] = value

    return result
