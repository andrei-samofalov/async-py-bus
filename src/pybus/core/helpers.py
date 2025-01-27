import asyncio
from concurrent.futures import Future


def handler_repr(handler):  # pragma: no cover
    """Return a string representation of the given handler."""
    cls = (
        handler.__self__.__class__.__name__ if hasattr(handler, "__self__")
        else handler.__class__.__name__ if hasattr(handler, "__class__")
        else ""
    )

    div = "." if cls else ""
    handler_name = f'{handler.__module__}.{cls}{div}'

    if hasattr(handler, '__name__'):
        handler_name += handler.__name__

    else:
        if "handle" in dir(handler):
            handler_name += 'handle'
        else:
            print(f'unknown handler {handler=!r}')
            print(dir(handler))

    return handler_name


def get_async_result(coro):
    """Waits async results in sync environment, decorators f.e."""
    loop = asyncio.get_event_loop()

    if not loop.is_running():
        return loop.run_until_complete(coro)

    future = Future()

    def _callback():
        asyncio.ensure_future(coro).add_done_callback(
            lambda task: future.set_result(task.result())
        )

    loop.call_soon_threadsafe(_callback)
    return future.result()
