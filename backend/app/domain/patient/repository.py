"""Patient repository interface."""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.domain.patient.aggregate import Patient
from app.domain.patient.value_objects import PhoneNumber, ABHANumber
from app.domain.shared.specification import Specification


class PatientRepository(ABC):
    """Abstract repository for Patient aggregate."""
    
    @abstractmethod
    async def find_by_id(self, patient_id: UUID) -> Optional[Patient]:
        """Find patient by ID."""
        pass
    
    @abstractmethod
    async def find_by_phone(self, phone: PhoneNumber) -> Optional[Patient]:
        """Find patient by phone number."""
        pass
    
    @abstractmethod
    async def find_by_abha(self, abha: ABHANumber) -> Optional[Patient]:
        """Find patient by ABHA number."""
        pass
    
    @abstractmethod
    async def find_by_specification(
        self,
        specification: Specification[Patient]
    ) -> List[Patient]:
        """Find patients matching specification."""
        pass
    
    @abstractmethod
    async def save(self, patient: Patient) -> None:
        """Save patient aggregate."""
        pass
    
    @abstractmethod
    async def update(self, patient: Patient) -> None:
        """Update patient aggregate with optimistic locking."""
        pass
    
    @abstractmethod
    async def delete(self, patient_id: UUID) -> None:
        """Delete patient (soft delete)."""
        pass
    
    @abstractmethod
    async def exists_by_phone(self, phone: PhoneNumber) -> bool:
        """Check if patient exists with phone number."""
        pass
    
    @abstractmethod
    async def exists_by_abha(self, abha: ABHANumber) -> bool:
        """Check if patient exists with ABHA number."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Count total patients."""
        pass
    
    @abstractmethod
    async def count_active(self) -> int:
        """Count active patients."""
        pass