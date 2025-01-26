from pybus.core import helpers

from . import __library_name__
from .api.typing import HandlerType, MessageType


class PyMessagesException(Exception):
    """base Exception"""
    reason: str = ""

    def __init__(self, message=None, **kwargs):
        for key, value in kwargs.items():
            if key == "handler" and not isinstance(value, str):
                value = helpers.handler_repr(value)

            setattr(self, key, value)

        self.message = message

    def get_message(self):  # pragma: no cover
        """Return the message for this exception"""
        return self.__doc__

    def with_reason(self, reason):
        """Return error with provided reason"""
        return self.__class__(**self.__dict__, reason=reason)

    def __str__(self):
        reason = f": {self.reason}" if self.reason else ""
        return f'{self.get_message()}{reason}'


class ImproperlyConfigured(PyMessagesException):
    """library configuration error."""

    def get_message(self):  # pragma: no cover
        return f'{__library_name__} configuration error'


class HandlerDoesNotExist(ImproperlyConfigured):
    """handler does not exist."""
    pymessage: MessageType

    def get_message(self):  # pragma: no cover
        return f'handler for {self.pymessage!r} does not exist'


class HandlerIsSync(ImproperlyConfigured):
    """handler is sync."""
    handler: HandlerType

    def get_message(self):  # pragma: no cover
        return f"handler {self.handler!r} is sync"


class HandlerSignatureError(ImproperlyConfigured):
    """handler signature error."""
    handler: HandlerType

    def get_message(self):  # pragma: no cover
        return f'handler {self.handler!r} has invalid signature'
