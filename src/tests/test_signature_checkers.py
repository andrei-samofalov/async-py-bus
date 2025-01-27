from typing import Protocol, runtime_checkable

import pytest

from pybus.core import exceptions as exc
from pybus.core.inspection import sig, utils


class BadAsync:
    def handle(self):
        pass


class BadNoMethod:
    pass


class BadSignature:
    async def handle(self):
        pass


class Good:
    async def handle(self, message: str):
        pass


async def handle(message: str):
    pass


class BadAssigned:
    pass


BadAssigned.handle = handle


@pytest.fixture(scope="module")
def protocol():
    @runtime_checkable
    class _Protocol(Protocol):
        async def handle(self, message: str):
            pass

    return _Protocol


async def handle(message: str):
    pass




@pytest.mark.parametrize(
    "message, handler, argname, kind, exception",
    (
        ("on_startup", None, "message", "pos", exc.HandlerDoesNotExist),
        ("on_startup", handle, None, "pos_or_kw", exc.ImproperlyConfigured),
        ("on_startup", handle, None, "kw_only", exc.ImproperlyConfigured),
        ("on_startup", handle, None, "kw", exc.ImproperlyConfigured),
        ("on_startup", handle, "message", "badkind", exc.ImproperlyConfigured),
    )
)
def test_check_signature_fails(message, handler, argname, kind, exception):
    with pytest.raises(exception):
        sig.check_signature(handler, message, argname)


@pytest.mark.parametrize(
    "cls, expected",
    (
        (BadAsync, False),
        (BadNoMethod, False),
        (Good, True),
        (BadSignature, False),
        (handle, False),
        (BadAssigned, False),
    )
)
def test_implements_protocol(cls, expected, protocol):
    result = utils.implements_protocol(cls, protocol)
    assert result is expected
