"""Patient specifications for queries."""
from datetime import datetime, timedelta

from app.domain.shared.specification import Specification
from app.domain.patient.aggregate import Patient


class ActivePatientsSpecification(Specification[Patient]):
    """Specification for active patients."""
    
    def is_satisfied_by(self, patient: Patient) -> bool:
        return patient.is_active


class VerifiedPatientsSpecification(Specification[Patient]):
    """Specification for verified patients."""
    
    def is_satisfied_by(self, patient: Patient) -> bool:
        return patient.is_verified


class MinorPatientsSpecification(Specification[Patient]):
    """Specification for minor patients."""
    
    def is_satisfied_by(self, patient: Patient) -> bool:
        return patient.is_minor


class SeniorPatientsSpecification(Specification[Patient]):
    """Specification for senior citizen patients."""
    
    def is_satisfied_by(self, patient: Patient) -> bool:
        return patient.is_senior


class PatientsWithABHASpecification(Specification[Patient]):
    """Specification for patients with ABHA number."""
    
    def is_satisfied_by(self, patient: Patient) -> bool:
        return patient.abha_number is not None


class RecentlyActiveSpecification(Specification[Patient]):
    """Specification for recently active patients."""
    
    def __init__(self, days: int = 30):
        self.cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    def is_satisfied_by(self, patient: Patient) -> bool:
        return patient.last_activity_at > self.cutoff_date


class PatientsWithConsentSpecification(Specification[Patient]):
    """Specification for patients with specific consent type."""
    
    def __init__(self, consent_type: str):
        self.consent_type = consent_type
    
    def is_satisfied_by(self, patient: Patient) -> bool:
        return patient.has_active_consent(self.consent_type)


class PatientsNeedingConsentRenewalSpecification(Specification[Patient]):
    """Specification for patients whose consents expire soon."""
    
    def __init__(self, days_before_expiry: int = 7):
        self.expiry_threshold = datetime.utcnow() + timedelta(days=days_before_expiry)
    
    def is_satisfied_by(self, patient: Patient) -> bool:
        for consent in patient.consents:
            if consent.is_active and consent.expires_at:
                if consent.expires_at <= self.expiry_threshold:
                    return True
        return False


class EligibleForTelehealthSpecification(Specification[Patient]):
    """Specification for patients eligible for telehealth."""
    
    def is_satisfied_by(self, patient: Patient) -> bool:
        # Must be active and verified
        if not patient.is_active or not patient.is_verified:
            return False
        
        # Must have telehealth consent
        if not patient.has_active_consent("telehealth"):
            return False
        
        # Minors need guardian consent
        if patient.is_minor and not patient.has_active_consent("guardian_consent"):
            return False
        
        return True