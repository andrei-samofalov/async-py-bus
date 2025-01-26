import typing as t


def hashable(value: t.Any) -> t.TypeGuard[t.Hashable]:
    """Direct way to check hashable"""
    try:
        hash(value)
        return True
    except TypeError:
        return False


@t.runtime_checkable
class _O(t.Protocol):
    pass


ProtocolType = type(_O)

del _O

EMPTY = object()
