import inspect
from typing import Any, NamedTuple, Optional

from pybus.core import exceptions as exc
from pybus.core.api.handlers import HandlerProtocol
from pybus.core.api.typing import HandlerType, Message
from pybus.core.inspection import utils
from pybus.core.types import EMPTY

KIND_MAP = {
    "pos_only": inspect.Parameter.POSITIONAL_ONLY,
    "pos_or_kw": inspect.Parameter.POSITIONAL_OR_KEYWORD,
    "pos": inspect.Parameter.VAR_POSITIONAL,
    "kw_only": inspect.Parameter.KEYWORD_ONLY,
    "kw": inspect.Parameter.VAR_KEYWORD,
}

KWSPEC = ("pos_or_kw", "kw_only", "kw")


class HandlerMetaData(NamedTuple):
    """Meta data for dispatcher"""
    handler: HandlerType
    inject: bool
    initkwargs: dict = {}
    argname: Optional[str] = EMPTY
    message: Optional[Message] = EMPTY


def check_signature(
    handler: HandlerType,
    message: Message = EMPTY,
    argname: Optional[str] = EMPTY,
    **initkwargs: dict[str, Any],
) -> HandlerMetaData:
    """Check signature of the handler"""
    if not handler:
        raise exc.HandlerDoesNotExist(pymessage=message)

    initkwargs = utils.unpack_initkwargs(**initkwargs)
    cls = handler
    if inspect.isclass(handler):
        cls = handler(**initkwargs)
        initkwargs = {}
        if utils.implements_protocol(cls, HandlerProtocol):
            handler = cls.handle
        else:
            if not hasattr(cls, "__call__"):
                raise exc.HandlerSignatureError(
                    handler=handler,
                    reason=f'class {cls.__class__.__name__} '
                           f'should implement `__call__` method or `HandlerProtocol`',
                )
            handler = cls.__call__

    if not inspect.iscoroutinefunction(handler):
        raise exc.HandlerIsSync(handler=cls, reason='accepted only awaitable')

    argposition = 0 if not utils.has_self(handler) else 1

    sig = inspect.signature(handler)
    param_amount = len(sig.parameters)

    if param_amount + argposition == argposition:
        # 1: существуют ли вообще аргументы
        # - если нет, то это норм, просто заканчиваем проверку,
        # а сообщение в хэндлер не передаем
        return HandlerMetaData(
            handler=handler, inject=False,
            message=message, initkwargs=initkwargs,
        )

    error = exc.HandlerSignatureError(pymessage=message, handler=handler)
    reason = None
    is_valid = False
    # todo annotated bind
    for index, param in enumerate(sig.parameters.values()):

        if index == param_amount - 1:
            # достигли конца цикла, необходимо прервать
            # просто дождаться - не вариант, т.к. используется конструкция for...else
            is_valid = True
            break

        if argname is EMPTY and index > argposition and param.kind in KIND_MAP:
            reason = (f"argument must be the first parameter if argname is not specified "
                      f"and kind of argument in {', '.join(KWSPEC)!r}")
            # 2: если аргументов больше, чем argpos, но мы не знаем имя аргумента,
            # при этом тип аргумента среди именных, ошибка-мы не сможем найти аргумент для вставки,
            # предложить указать argname
            break

        if argname != param.name:
            # 3. Имя указано, но не соответствует аргументу, пропускаем
            continue

    else:
        # for-loop did not find compatible argument in the handler signature
        reason = f'argname {argname!r} not found'

    if is_valid is False:
        raise error.with_reason(reason=reason)

    return HandlerMetaData(
        handler=cls, inject=True, argname=argname,
        message=message, initkwargs=initkwargs,
    )
