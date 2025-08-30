"""Base Entity class following DDD principles."""
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List
from uuid import UUID, uuid4


@dataclass
class DomainEvent:
    """Base class for domain events."""
    aggregate_id: UUID
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = field(init=False)
    
    def __post_init__(self):
        self.event_type = self.__class__.__name__


class Entity(ABC):
    """Base class for all domain entities."""
    
    def __init__(self, id: UUID = None):
        self._id = id or uuid4()
        self._events: List[DomainEvent] = []
    
    @property
    def id(self) -> UUID:
        """Entity identifier."""
        return self._id
    
    def add_domain_event(self, event: DomainEvent) -> None:
        """Add a domain event to be dispatched."""
        self._events.append(event)
    
    def clear_domain_events(self) -> List[DomainEvent]:
        """Clear and return all domain events."""
        events = self._events.copy()
        self._events.clear()
        return events
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Entity):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        return hash(self._id)