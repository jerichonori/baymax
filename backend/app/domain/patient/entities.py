"""Patient domain entities."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.domain.shared.entity import Entity, DomainEvent
from app.domain.patient.value_objects import (
    PhoneNumber, EmailAddress, ABHANumber, PatientName,
    DateOfBirth, Gender, Address
)


class PatientRegisteredEvent(DomainEvent):
    """Event raised when a new patient is registered."""
    
    def __init__(self, patient_id: UUID, phone: PhoneNumber, name: PatientName):
        super().__init__(aggregate_id=patient_id)
        self.phone = phone
        self.name = name


class PatientVerifiedEvent(DomainEvent):
    """Event raised when a patient is verified."""
    
    def __init__(self, patient_id: UUID, verification_method: str):
        super().__init__(aggregate_id=patient_id)
        self.verification_method = verification_method


class ConsentGrantedEvent(DomainEvent):
    """Event raised when patient grants consent."""
    
    def __init__(self, patient_id: UUID, consent_type: str, purpose: str):
        super().__init__(aggregate_id=patient_id)
        self.consent_type = consent_type
        self.purpose = purpose


class ConsentRevokedEvent(DomainEvent):
    """Event raised when patient revokes consent."""
    
    def __init__(self, patient_id: UUID, consent_type: str):
        super().__init__(aggregate_id=patient_id)
        self.consent_type = consent_type


class Consent(Entity):
    """Consent entity representing patient's consent for data processing."""
    
    def __init__(
        self,
        id: UUID,
        patient_id: UUID,
        consent_type: str,
        purpose: str,
        granted_at: datetime,
        expires_at: Optional[datetime] = None,
        revoked_at: Optional[datetime] = None
    ):
        super().__init__(id)
        self.patient_id = patient_id
        self.consent_type = consent_type
        self.purpose = purpose
        self.granted_at = granted_at
        self.expires_at = expires_at
        self.revoked_at = revoked_at
    
    @property
    def is_active(self) -> bool:
        """Check if consent is currently active."""
        if self.revoked_at:
            return False
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def revoke(self) -> None:
        """Revoke this consent."""
        if self.revoked_at:
            raise ValueError("Consent already revoked")
        self.revoked_at = datetime.utcnow()
    
    def extend(self, new_expiry: datetime) -> None:
        """Extend consent expiry."""
        if not self.is_active:
            raise ValueError("Cannot extend inactive consent")
        if new_expiry <= datetime.utcnow():
            raise ValueError("New expiry must be in the future")
        self.expires_at = new_expiry


class EmergencyContact(Entity):
    """Emergency contact entity."""
    
    def __init__(
        self,
        id: UUID,
        name: PatientName,
        phone: PhoneNumber,
        relationship: str,
        is_primary: bool = False
    ):
        super().__init__(id)
        self.name = name
        self.phone = phone
        self.relationship = relationship
        self.is_primary = is_primary
    
    def make_primary(self) -> None:
        """Mark this contact as primary."""
        self.is_primary = True
    
    def update_phone(self, new_phone: PhoneNumber) -> None:
        """Update contact phone number."""
        self.phone = new_phone


class MedicalHistory:
    """Medical history value object."""
    
    def __init__(
        self,
        chronic_conditions: List[str] = None,
        allergies: List[str] = None,
        current_medications: List[str] = None,
        past_surgeries: List[str] = None,
        family_history: List[str] = None
    ):
        self.chronic_conditions = chronic_conditions or []
        self.allergies = allergies or []
        self.current_medications = current_medications or []
        self.past_surgeries = past_surgeries or []
        self.family_history = family_history or []
    
    def add_allergy(self, allergy: str) -> None:
        """Add a new allergy."""
        if allergy not in self.allergies:
            self.allergies.append(allergy)
    
    def add_medication(self, medication: str) -> None:
        """Add a current medication."""
        if medication not in self.current_medications:
            self.current_medications.append(medication)
    
    def remove_medication(self, medication: str) -> None:
        """Remove a medication."""
        if medication in self.current_medications:
            self.current_medications.remove(medication)
    
    @property
    def has_allergies(self) -> bool:
        """Check if patient has any allergies."""
        return len(self.allergies) > 0
    
    @property
    def has_chronic_conditions(self) -> bool:
        """Check if patient has chronic conditions."""
        return len(self.chronic_conditions) > 0