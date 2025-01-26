import typing as t


@t.runtime_checkable
class DescriptorProtocol(t.Protocol):
    """Descriptor protocol."""

    def __get__(self, instance, owner): ...

    def __set__(self, instance, value): ...

    def __delete__(self, instance): ...
