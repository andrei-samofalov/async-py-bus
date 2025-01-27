import abc
import inspect
import typing as t
from collections import defaultdict
from logging import getLogger

from pybus.core import exceptions as exc
from pybus.core import helpers

logger = getLogger(__name__)

ProvidedType = t.Any
ProviderFn = t.Callable[[], t.Awaitable[ProvidedType] | ProvidedType]
ProviderItem = dict[str, ProviderFn | t.Optional[ProvidedType]]


class Provider(metaclass=abc.ABCMeta):
    """Base dependency provider."""

    providers: dict[str, ProviderItem] = defaultdict(dict)

    @classmethod
    def _func_call(cls, fn: ProviderFn) -> ProvidedType:
        """Call func"""

        if inspect.iscoroutinefunction(fn):
            return helpers.get_async_result(fn())

        return fn()

    @classmethod
    def _get_provider(cls, name: str) -> ProviderItem:
        if (provided := cls.providers.get(name, None)) is None:
            raise KeyError(name)

        return provided

    @classmethod
    @abc.abstractmethod
    def get_provided(cls, provider: ProviderItem) -> ProvidedType:
        """Return provided object"""

    @classmethod
    def call(cls, name: str) -> ProvidedType:
        """Call the provider."""
        provided = cls._get_provider(name)
        return cls.get_provided(provided)

    def __class_getitem__(cls, item: ProviderFn):
        if isinstance(item, slice):
            name, fn = str(item.start), item.stop
        else:
            raise TypeError(
                f"{type(item)} not supported for {cls.__name__} generic, "
                f"use slice syntax: fn_name: fn"
            )

        if name in cls.providers:
            if (cls_type := cls.providers[name]['type']) != cls.__name__:
                raise exc.ImproperlyConfigured(
                    reason=f'attempt to reassign provider class from {cls_type} to {cls.__name__}'
                )
            return cls

        cls.providers[name] = {
            "item": fn,
            "raw": True,
            "type": cls.__name__,
        }
        return cls


class Singleton(Provider):
    """Singleton dependency provider."""

    @classmethod
    def get_provided(cls, provider: ProviderItem) -> ProvidedType:
        provided = provider['item']

        if provider['raw'] is False:
            return provided

        provided = provider['item'] = cls._func_call(provided)
        provider['raw'] = False

        return provided


class Factory(Provider):
    """Factory dependency provider."""

    @classmethod
    def get_provided(cls, provider: ProviderItem) -> ProvidedType:
        """Call the provider."""
        return cls._func_call(provider['item'])
