"""Patient aggregate root."""
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID

from app.domain.shared.aggregate_root import AggregateRoot
from app.domain.patient.entities import (
    Consent, EmergencyContact, MedicalHistory,
    PatientRegisteredEvent, PatientVerifiedEvent,
    ConsentGrantedEvent, ConsentRevokedEvent
)
from app.domain.patient.value_objects import (
    PhoneNumber, EmailAddress, ABHANumber, PatientName,
    DateOfBirth, Gender, Address
)


class Patient(AggregateRoot):
    """Patient aggregate root - maintains patient invariants."""
    
    def __init__(
        self,
        id: UUID,
        phone: PhoneNumber,
        name: PatientName,
        date_of_birth: DateOfBirth,
        gender: Gender,
        email: Optional[EmailAddress] = None,
        abha_number: Optional[ABHANumber] = None,
        address: Optional[Address] = None,
        language_preference: str = "en",
        version: int = 0
    ):
        super().__init__(id, version)
        self.phone = phone
        self.name = name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.email = email
        self.abha_number = abha_number
        self.address = address
        self.language_preference = language_preference
        
        # Entity collections
        self.consents: List[Consent] = []
        self.emergency_contacts: List[EmergencyContact] = []
        self.medical_history = MedicalHistory()
        
        # Status fields
        self.is_verified = False
        self.is_active = True
        self.registered_at = datetime.utcnow()
        self.verified_at: Optional[datetime] = None
        self.last_activity_at = datetime.utcnow()
    
    @classmethod
    def register(
        cls,
        id: UUID,
        phone: PhoneNumber,
        name: PatientName,
        date_of_birth: DateOfBirth,
        gender: Gender,
        email: Optional[EmailAddress] = None
    ) -> 'Patient':
        """Factory method to register a new patient."""
        patient = cls(
            id=id,
            phone=phone,
            name=name,
            date_of_birth=date_of_birth,
            gender=gender,
            email=email
        )
        
        # Raise domain event
        patient.add_domain_event(
            PatientRegisteredEvent(
                patient_id=id,
                phone=phone,
                name=name
            )
        )
        
        return patient
    
    def verify(self, method: str = "otp") -> None:
        """Verify the patient's identity."""
        if self.is_verified:
            raise ValueError("Patient already verified")
        
        self.is_verified = True
        self.verified_at = datetime.utcnow()
        self.increment_version()
        
        # Raise domain event
        self.add_domain_event(
            PatientVerifiedEvent(
                patient_id=self.id,
                verification_method=method
            )
        )
    
    def grant_consent(
        self,
        consent_id: UUID,
        consent_type: str,
        purpose: str,
        expires_at: Optional[datetime] = None
    ) -> Consent:
        """Grant consent for data processing."""
        # Check if similar consent already exists and is active
        for consent in self.consents:
            if consent.consent_type == consent_type and consent.is_active:
                raise ValueError(f"Active consent for {consent_type} already exists")
        
        consent = Consent(
            id=consent_id,
            patient_id=self.id,
            consent_type=consent_type,
            purpose=purpose,
            granted_at=datetime.utcnow(),
            expires_at=expires_at
        )
        
        self.consents.append(consent)
        self.increment_version()
        
        # Raise domain event
        self.add_domain_event(
            ConsentGrantedEvent(
                patient_id=self.id,
                consent_type=consent_type,
                purpose=purpose
            )
        )
        
        return consent
    
    def revoke_consent(self, consent_type: str) -> None:
        """Revoke consent for a specific type."""
        consent_found = False
        for consent in self.consents:
            if consent.consent_type == consent_type and consent.is_active:
                consent.revoke()
                consent_found = True
                self.increment_version()
                
                # Raise domain event
                self.add_domain_event(
                    ConsentRevokedEvent(
                        patient_id=self.id,
                        consent_type=consent_type
                    )
                )
                break
        
        if not consent_found:
            raise ValueError(f"No active consent found for {consent_type}")
    
    def add_emergency_contact(
        self,
        contact_id: UUID,
        name: PatientName,
        phone: PhoneNumber,
        relationship: str,
        is_primary: bool = False
    ) -> EmergencyContact:
        """Add an emergency contact."""
        # Validate invariants
        if is_primary:
            # Only one primary contact allowed
            for contact in self.emergency_contacts:
                if contact.is_primary:
                    contact.is_primary = False
        
        contact = EmergencyContact(
            id=contact_id,
            name=name,
            phone=phone,
            relationship=relationship,
            is_primary=is_primary
        )
        
        self.emergency_contacts.append(contact)
        self.increment_version()
        
        return contact
    
    def update_contact_info(
        self,
        phone: Optional[PhoneNumber] = None,
        email: Optional[EmailAddress] = None,
        address: Optional[Address] = None
    ) -> None:
        """Update patient contact information."""
        if phone:
            self.phone = phone
        if email:
            self.email = email
        if address:
            self.address = address
        
        self.last_activity_at = datetime.utcnow()
        self.increment_version()
    
    def link_abha(self, abha_number: ABHANumber) -> None:
        """Link ABHA number to patient profile."""
        if self.abha_number:
            raise ValueError("ABHA number already linked")
        
        self.abha_number = abha_number
        self.increment_version()
    
    def deactivate(self) -> None:
        """Deactivate patient account."""
        if not self.is_active:
            raise ValueError("Patient already deactivated")
        
        self.is_active = False
        self.increment_version()
    
    def reactivate(self) -> None:
        """Reactivate patient account."""
        if self.is_active:
            raise ValueError("Patient already active")
        
        self.is_active = True
        self.last_activity_at = datetime.utcnow()
        self.increment_version()
    
    def has_active_consent(self, consent_type: str) -> bool:
        """Check if patient has active consent for a type."""
        for consent in self.consents:
            if consent.consent_type == consent_type and consent.is_active:
                return True
        return False
    
    def get_active_consents(self) -> List[Consent]:
        """Get all active consents."""
        return [c for c in self.consents if c.is_active]
    
    def get_primary_emergency_contact(self) -> Optional[EmergencyContact]:
        """Get primary emergency contact."""
        for contact in self.emergency_contacts:
            if contact.is_primary:
                return contact
        return self.emergency_contacts[0] if self.emergency_contacts else None
    
    def validate_invariants(self) -> None:
        """Validate patient aggregate invariants."""
        # Invariant: Patient must be verified to have ABHA
        if self.abha_number and not self.is_verified:
            raise ValueError("Patient must be verified to link ABHA")
        
        # Invariant: Minor patients must have emergency contact
        if self.date_of_birth.is_minor and not self.emergency_contacts:
            raise ValueError("Minor patients must have emergency contact")
        
        # Invariant: Only one primary emergency contact
        primary_count = sum(1 for c in self.emergency_contacts if c.is_primary)
        if primary_count > 1:
            raise ValueError("Only one primary emergency contact allowed")
        
        # Invariant: Deactivated patients cannot be modified
        if not self.is_active and self._version > 0:
            raise ValueError("Cannot modify deactivated patient")
    
    @property
    def age(self) -> int:
        """Get patient's current age."""
        return self.date_of_birth.age
    
    @property
    def is_minor(self) -> bool:
        """Check if patient is a minor."""
        return self.date_of_birth.is_minor
    
    @property
    def is_senior(self) -> bool:
        """Check if patient is a senior citizen."""
        return self.date_of_birth.is_senior
    
    @property
    def full_name(self) -> str:
        """Get patient's full name."""
        return self.name.full_name
    
    @property
    def masked_phone(self) -> str:
        """Get masked phone number."""
        return self.phone.masked
    
    @property
    def masked_email(self) -> str:
        """Get masked email."""
        return self.email.masked if self.email else ""