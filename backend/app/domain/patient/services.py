"""Patient domain services."""
from typing import Optional, List
from uuid import UUID, uuid4

from app.domain.patient.aggregate import Patient
from app.domain.patient.repository import PatientRepository
from app.domain.patient.value_objects import (
    PhoneNumber, EmailAddress, PatientName,
    DateOfBirth, Gender, ABHANumber
)
from app.domain.patient.specifications import (
    ActivePatientsSpecification,
    VerifiedPatientsSpecification,
    MinorPatientsSpecification
)


class PatientDuplicationChecker:
    """Domain service to check for patient duplication."""
    
    def __init__(self, repository: PatientRepository):
        self.repository = repository
    
    async def is_duplicate_phone(self, phone: PhoneNumber) -> bool:
        """Check if phone number is already registered."""
        return await self.repository.exists_by_phone(phone)
    
    async def is_duplicate_abha(self, abha: ABHANumber) -> bool:
        """Check if ABHA number is already registered."""
        return await self.repository.exists_by_abha(abha)
    
    async def find_existing_patient(
        self,
        phone: PhoneNumber,
        abha: Optional[ABHANumber] = None
    ) -> Optional[Patient]:
        """Find existing patient by phone or ABHA."""
        # Check by phone first
        patient = await self.repository.find_by_phone(phone)
        if patient:
            return patient
        
        # Check by ABHA if provided
        if abha:
            patient = await self.repository.find_by_abha(abha)
            if patient:
                return patient
        
        return None


class PatientRegistrationService:
    """Domain service for patient registration."""
    
    def __init__(
        self,
        repository: PatientRepository,
        duplication_checker: PatientDuplicationChecker
    ):
        self.repository = repository
        self.duplication_checker = duplication_checker
    
    async def register_patient(
        self,
        phone: PhoneNumber,
        name: PatientName,
        date_of_birth: DateOfBirth,
        gender: Gender,
        email: Optional[EmailAddress] = None,
        abha: Optional[ABHANumber] = None
    ) -> Patient:
        """Register a new patient with deduplication check."""
        # Check for existing patient
        existing = await self.duplication_checker.find_existing_patient(phone, abha)
        if existing:
            raise ValueError(f"Patient already exists with phone {phone.masked}")
        
        # Create new patient
        patient = Patient.register(
            id=uuid4(),
            phone=phone,
            name=name,
            date_of_birth=date_of_birth,
            gender=gender,
            email=email
        )
        
        # Link ABHA if provided
        if abha:
            # For new registration, we can link ABHA before verification
            # as it's part of the registration process
            patient.abha_number = abha
        
        # Save patient
        await self.repository.save(patient)
        
        return patient


class PatientConsentService:
    """Domain service for managing patient consents."""
    
    def __init__(self, repository: PatientRepository):
        self.repository = repository
    
    async def grant_intake_consent(
        self,
        patient_id: UUID,
        purpose: str = "AI-assisted medical intake"
    ) -> None:
        """Grant consent for AI intake processing."""
        patient = await self.repository.find_by_id(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        # Grant consent for intake
        patient.grant_consent(
            consent_id=uuid4(),
            consent_type="ai_intake",
            purpose=purpose
        )
        
        # Grant consent for data processing
        patient.grant_consent(
            consent_id=uuid4(),
            consent_type="data_processing",
            purpose="Process medical information for healthcare delivery"
        )
        
        await self.repository.update(patient)
    
    async def check_intake_consent(self, patient_id: UUID) -> bool:
        """Check if patient has consent for AI intake."""
        patient = await self.repository.find_by_id(patient_id)
        if not patient:
            return False
        
        return patient.has_active_consent("ai_intake")
    
    async def revoke_all_consents(self, patient_id: UUID) -> None:
        """Revoke all patient consents."""
        patient = await self.repository.find_by_id(patient_id)
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        # Revoke all active consents
        for consent in patient.get_active_consents():
            patient.revoke_consent(consent.consent_type)
        
        await self.repository.update(patient)


class PatientEligibilityService:
    """Domain service to check patient eligibility for services."""
    
    def __init__(self, repository: PatientRepository):
        self.repository = repository
    
    async def is_eligible_for_telehealth(self, patient_id: UUID) -> bool:
        """Check if patient is eligible for telehealth services."""
        patient = await self.repository.find_by_id(patient_id)
        if not patient:
            return False
        
        # Check eligibility criteria
        if not patient.is_active:
            return False
        
        if not patient.is_verified:
            return False
        
        if not patient.has_active_consent("telehealth"):
            return False
        
        # Minors need guardian consent
        if patient.is_minor and not patient.has_active_consent("guardian_consent"):
            return False
        
        return True
    
    async def is_eligible_for_ai_intake(self, patient_id: UUID) -> bool:
        """Check if patient is eligible for AI intake."""
        patient = await self.repository.find_by_id(patient_id)
        if not patient:
            return False
        
        # Check eligibility criteria
        if not patient.is_active:
            return False
        
        if not patient.has_active_consent("ai_intake"):
            return False
        
        # Additional checks for minors
        if patient.is_minor:
            # Must have emergency contact
            if not patient.emergency_contacts:
                return False
            # Must have guardian consent
            if not patient.has_active_consent("guardian_consent"):
                return False
        
        return True


class PatientSearchService:
    """Domain service for searching patients."""
    
    def __init__(self, repository: PatientRepository):
        self.repository = repository
    
    async def find_active_patients(self) -> List[Patient]:
        """Find all active patients."""
        spec = ActivePatientsSpecification()
        return await self.repository.find_by_specification(spec)
    
    async def find_verified_patients(self) -> List[Patient]:
        """Find all verified patients."""
        spec = VerifiedPatientsSpecification()
        return await self.repository.find_by_specification(spec)
    
    async def find_minor_patients(self) -> List[Patient]:
        """Find all minor patients."""
        spec = MinorPatientsSpecification()
        return await self.repository.find_by_specification(spec)
    
    async def find_patients_needing_consent_renewal(self) -> List[Patient]:
        """Find patients whose consents are expiring soon."""
        # This would use a more complex specification
        # checking consent expiry dates
        pass