import asyncio
import signal
from logging import getLogger

prepare_shutdown = asyncio.Event()
logger = getLogger(__name__)
logger.setLevel("DEBUG")


def _handle_shutdown(sig):
    logger.debug(f"received {sig.name}, shutting down")
    prepare_shutdown.set()


def _create_listeners():
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, _handle_shutdown, sig
        )


def setup():
    """Setup library graceful shutdown."""
    _create_listeners()


async def wait_for_shutdown():
    """Alias to the shutdown event"""
    await prepare_shutdown.wait()
