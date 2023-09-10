"""Sample module."""

from budosystems.models.core import Entity
from budosystems.events.base import Event

class MyEntity(Entity):
    """A new `Entity` for this subproject."""
    a_field: int

class MyEvent(Event):
    """A new `Event` type for this subproject."""
