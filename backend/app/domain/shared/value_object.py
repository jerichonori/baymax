"""Base Value Object class following DDD principles."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class ValueObject(ABC):
    """Base class for value objects."""
    
    @abstractmethod
    def validate(self) -> None:
        """Validate the value object's state."""
        pass
    
    def __post_init__(self):
        """Validate after initialization."""
        self.validate()
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))