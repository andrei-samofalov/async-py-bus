```python
import dataclasses
from typing import ClassVar, Any


# defining domain model
@dataclasses.dataclass
class Book:
    """Book model"""
    title: str
    author: str
    year: int


# defining application message models
@dataclasses.dataclass(frozen=True, slots=True)
class Message:
    """Application Message model"""
    __dataclass_fields__: ClassVar[dict[str, Any]]


@dataclasses.dataclass(frozen=True, slots=True)
class Event(Message):
    """Application Event model"""


@dataclasses.dataclass(frozen=True, slots=True)
class Command(Message):
    """Application Command model"""


@dataclasses.dataclass(frozen=True, slots=True)
class Query(Message):
    """Application Query model"""

```