from pybus.core.api.typing import MessageTypefrom pybus.core.api.typing import ReturnType

#### Basic usage

```python
import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from typing import AsyncContextManager

from pybus import dispatcher as dp, AbstractHandler


@dp.events.register('on startup')
@dp.events.register('on message received')
async def on_startup(event):
    # do some on startup
    print(f"got {event} event")


@dataclass
class Event:
    name: str
    somelogiccalue: str


class CustomHandler:

    async def __call__(self, event: Event):
        print(f'got {event} event')


@dataclass
class Command:
    dosomething: bool


@dp.commands.register(Event, session_factory=Provide['session_factory'])
class AnotherCustomHandler:

    def __init__(self, session_factory: Callable[[], AsyncContextManager[AsyncSession]]):
        self._session_factory = session_factory

    async def handle(self, command: Command) -> None:
        async with self._session_factory() as session:
            print(f'got {command} command and session is provided!')
            # do something with session


class YetAnotherHandler(AbstractHandler):

    async def handle(self, command: Command):
        print(f'got {command} message')
        await self.add_event('on command received')


async def main():
    dp.start()
    
    dp.commands.bind(Command, YetAnotherHandler)
    # or
    # dp.commands.bind(Command, YetAnotherHandler().handle)
    # or
    # dp.register_command_handler(Command, YetAnotherHandler)
    # and decorator ofc... Choose your best way!
    
    await dp.events.send(Event(name='someevent', somelogiccalue='emit'))
    await dp.commands.send(Command(dosomething=True))

    await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(main())
```
