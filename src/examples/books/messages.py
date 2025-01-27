import dataclasses

from examples.books.models import Book, Command, Query, Event


# defining simple messages: command, event and query
@dataclasses.dataclass(frozen=True, slots=True)
class BookCreated(Event):
    """Book created event"""
    book: Book


@dataclasses.dataclass(frozen=True, slots=True)
class CreateBook(Book, Command):
    """Create book Command"""


@dataclasses.dataclass(frozen=True, slots=True)
class BookQuery(Query):
    """Book Query model"""
    title: str


@dataclasses.dataclass(frozen=True, slots=True)
class BookQueryResult(Event):
    """Book Query result model"""
    books: list[Book] = dataclasses.field(default_factory=list)
