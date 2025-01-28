# async-py-bus

The library is designed for asynchronous `event-driven` and `cqrs` Python projects,
has no third-party dependencies, and is useful for handling domain events, queries and commands.

See [more examples](https://github.com/andrei-samofalov/async-py-bus/tree/master/docs/examples) on
GitHub

## Basic usage

The core of the library is the `Dispatcher` class.
It handles three types of messages: `events`, `commands` and `queries`.

### Dispatcher initializing

You can use the default object from `pybus`

```python
from pybus import dispatcher as dp
```

Note that the query engine is not enabled in the default implementation.
Therefore, if your application uses queries you need to instantiate the `Dispatcher` class 
with an additional parameter:

```python
from pybus import Dispatcher, RequestRouter

dp = Dispatcher(
    queries_router_cls=RequestRouter,
)
```

### Handlers` signature

A basic handler is an asynchronous function that takes either one or zero arguments.

```python
async def handler_with_arg(event: EventType):
    # do something with event...

async def handler_without_arg():
    # do something
```

Additionally, a handler can accept any number of keyword arguments (how to pass them to the handler
is explained below). However, if the parameter expecting the message is strictly positional,
you must specify the `argname` parameter when registering the handler.

A handler can also be a class implementing the `HandlerProtocol` protocol or
an asynchronous `__call__` method.
The signature rules for the `handle` or `__call__` methods are the same as for a regular function.

```python
class HandlerProtocol(Protocol):

    async def handle(self, message: MessageType, **kwargs) -> Any:
        """Handle message."""

    async def add_event(self, event: EventType) -> None:
        """Add event to emit later."""

    async def dump_events(self) -> list[EventType]:
        """Return list of collected events."""
```

If your class needs some initialization parameters, you can specify them during handler
registration as named argument pairs.
These arguments will be passed directly to the class’s `__init__` method
(make sure there are no strictly positional arguments).

```python
class CustomHandler:
    def __init__(self, repo: RepoType):
        self._repo = repo

    async def __call__(self, cmd: CreateUserCommand):
        user = await self._repo.create(cmd.data)
        return UserCreated(data=user)
```

The same behavior applies if the handler is a simple function but takes more than one parameter
without default values.

```python
async def create_user_handler(cmd: CreateUserCommand, repo: RepoType):
    user = await repo.create(cmd.data)
    return UserCreated(data=user)


# main.py
user_repo = UserRepoImpl()
dp.commands.bind(CreateUserCommand, handler=create_user_handler, repo=user_repo)
```

You may notice that both the `create_user_handler` function and the `__call__` method of
the `CustomHandler` class return an event.
This allows you to pass new outgoing events to the dispatcher, which will forward them
to the appropriate handler.
In the case of a class implementing `HandlerProtocol`, additionally events can be added during 
processing inside the `handle` method.

### Handlers binding

We’ve talked a lot about how to declare handlers; now let’s register them.

Currently, there are several ways to do this:

* Pass the handler to the dispatcher’s `register_<message>_handler` method,
  where `<message>` is one of `event`, `command`, or `query`.
  ```python
  dp.register_event_handler(UserCreated, create_user_handler)
  ```
* Use the `bind` method of one of the dispatcher’s routers (`dp.events`, `dp.commands`,
  `dp.queries`).
  ```python
  dp.events.bind(UserCreated, create_user_handler)
  ```
* Use the `register` decorator from one of the dispatcher’s routers (`dp.events`, `dp.commands`,
  `dp.queries`).
  ```python
  @dp.events.register(UserCreated)
  async def create_user_handler(event): ...
  ```

### Dispatcher start

After registering the handlers, you just need to start the dispatcher:

```python
dp.start()
```

During this operation, the handler map will be finalized,
and you won’t be able to register new handlers. Please keep this in mind.

### Utils

For simple `dependency injection`, the library provides two classes: `Singleton` and `Factory`.
They use the `slice-syntax`: the name of the resource and the `callable` that retrieves it
(can be either synchronous or asynchronous).

In general, there are more convenient and optimized libraries for this task.

```python
def get_user_repo() -> UserRepo: ...


@dp.queries.register(UserQuery, repo=Singleton["repo": get_user_repo])
async def book_query_handler(query: UserQuery, repo: UserRepo) -> BookQueryResult: ...
```

###### The docs are being updated...
