"""Aggregate Root base class following DDD principles."""
from typing import List
from uuid import UUID

from app.domain.shared.entity import Entity, DomainEvent


class AggregateRoot(Entity):
    """Base class for aggregate roots."""
    
    def __init__(self, id: UUID = None, version: int = 0):
        super().__init__(id)
        self._version = version
    
    @property
    def version(self) -> int:
        """Aggregate version for optimistic locking."""
        return self._version
    
    def increment_version(self) -> None:
        """Increment version for optimistic locking."""
        self._version += 1
    
    def validate_invariants(self) -> None:
        """
        Validate aggregate invariants.
        Override in subclasses to enforce business rules.
        """
        pass