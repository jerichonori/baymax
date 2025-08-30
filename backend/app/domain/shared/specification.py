"""Specification pattern for domain queries."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')


class Specification(ABC, Generic[T]):
    """Base specification for domain queries."""
    
    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if the specification is satisfied by the candidate."""
        pass
    
    def and_(self, other: 'Specification[T]') -> 'AndSpecification[T]':
        """Create an AND specification."""
        return AndSpecification(self, other)
    
    def or_(self, other: 'Specification[T]') -> 'OrSpecification[T]':
        """Create an OR specification."""
        return OrSpecification(self, other)
    
    def not_(self) -> 'NotSpecification[T]':
        """Create a NOT specification."""
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    """AND combination of specifications."""
    
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


class OrSpecification(Specification[T]):
    """OR combination of specifications."""
    
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left = left
        self.right = right
    
    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)


class NotSpecification(Specification[T]):
    """NOT specification."""
    
    def __init__(self, spec: Specification[T]):
        self.spec = spec
    
    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)