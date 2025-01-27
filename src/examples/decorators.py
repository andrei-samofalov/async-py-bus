import asyncio
import dataclasses
import logging

from examples.books.messages import CreateBook, BookCreated, BookQuery, BookQueryResult
from examples.books.models import Book
from pybus import Dispatcher, RequestRouter
from pybus.core.dependency.providers import Singleton, Factory

dp = Dispatcher(
    queries_router_cls=RequestRouter,  # by default query router is disabled
)


async def get_storage():
    """Dependency injection of storage."""
    return {}


# somewhere in your code
@dp.commands.register(CreateBook, storage=Singleton["storage": get_storage])
# ensure Singleton dependency name is the same that in handler's args
async def create_book_handler(command: CreateBook, storage: dict) -> BookCreated:
    """Create book"""

    # simplify for example
    print(f'got command {command}')
    book = Book(**dataclasses.asdict(command))
    storage[book.title] = book

    # returning the event leads to emitting it by the dispatcher,
    # another way to do that will be described in classes example
    return BookCreated(book=book)


@dp.events.register(BookCreated)
async def book_created_handler(event: BookCreated) -> None:
    """Handle book creation"""
    print(f'got event {event}')


@dp.queries.register(BookQuery, storage=Factory["storage": get_storage])
async def book_query_handler(query: BookQuery, storage: dict) -> BookQueryResult:
    """Handle book query"""
    # find books in storage...
    books = [book for title, book in storage.items() if title == query.title]
    print(f"got query {query}, found {len(books)} books")
    return BookQueryResult(books=books)


@dp.events.register(BookQueryResult)
async def listen_query(event: BookQueryResult) -> None:
    """Listen query result handler"""
    print(f'query result: {event}')


@dp.events.register('on startup')
# # you can also use strings for message identifiers
async def on_start() -> None:
    """Handlers without message argument also can be used"""
    # do something on startup
    print('application started')


async def main() -> None:
    """Application entrypoint"""
    logging.basicConfig(level=logging.DEBUG)

    dp.start()  # start router's engines

    await dp.events.send('on startup')
    await dp.commands.send(
        CreateBook(title="Philosopher's Stone", author="J. K. Rowling", year=1997)
    )
    await dp.queries.send(
        BookQuery(title="Philosopher's Stone")
    )

    await asyncio.sleep(0.1)  # give app some time to proceed


if __name__ == '__main__':
    asyncio.run(main())
