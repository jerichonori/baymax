"""Value objects for Intake domain."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class IntakeStatus(Enum):
    """Intake session status."""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    ESCALATED = "escalated"


class ConversationType(Enum):
    """Type of conversation interface."""
    TEXT = "text"
    VOICE = "voice"
    VIDEO = "video"


class RedFlagSeverity(Enum):
    """Severity levels for red flags."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafetyCheckResult(Enum):
    """Result of safety check."""
    SAFE = "safe"
    BLOCKED = "blocked"
    WARNING = "warning"


@dataclass(frozen=True)
class Language:
    """Language value object."""
    
    code: str
    name: str
    confidence: float = 1.0
    
    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "te": "Telugu",
        "ta": "Tamil",
        "kn": "Kannada",
        "ml": "Malayalam",
        "bn": "Bengali",
        "gu": "Gujarati",
        "mr": "Marathi",
        "pa": "Punjabi",
        "ur": "Urdu"
    }
    
    def __post_init__(self):
        if self.code not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {self.code}")
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Invalid confidence: {self.confidence}")


@dataclass(frozen=True)
class ChiefComplaint:
    """Chief complaint value object."""
    
    description: str
    duration: Optional[str] = None
    severity: Optional[int] = None  # 1-10 scale
    onset: Optional[str] = None
    
    def __post_init__(self):
        if not self.description or len(self.description.strip()) < 3:
            raise ValueError("Chief complaint description too short")
        if self.severity is not None and not 1 <= self.severity <= 10:
            raise ValueError("Severity must be between 1 and 10")


@dataclass(frozen=True)
class Symptom:
    """Individual symptom value object."""
    
    name: str
    duration: Optional[str] = None
    severity: Optional[int] = None  # 1-10 scale
    frequency: Optional[str] = None
    aggravating_factors: List[str] = None
    relieving_factors: List[str] = None
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Symptom name is required")
        if self.severity is not None and not 1 <= self.severity <= 10:
            raise ValueError("Severity must be between 1 and 10")


@dataclass(frozen=True)
class VitalSigns:
    """Vital signs value object."""
    
    temperature: Optional[float] = None  # Celsius
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    heart_rate: Optional[int] = None  # bpm
    respiratory_rate: Optional[int] = None  # per minute
    oxygen_saturation: Optional[int] = None  # percentage
    weight: Optional[float] = None  # kg
    height: Optional[float] = None  # cm
    
    def __post_init__(self):
        # Validate temperature
        if self.temperature is not None:
            if not 35 <= self.temperature <= 42:
                raise ValueError(f"Invalid temperature: {self.temperature}")
        
        # Validate blood pressure
        if self.blood_pressure_systolic is not None:
            if not 60 <= self.blood_pressure_systolic <= 250:
                raise ValueError(f"Invalid systolic BP: {self.blood_pressure_systolic}")
        
        if self.blood_pressure_diastolic is not None:
            if not 40 <= self.blood_pressure_diastolic <= 150:
                raise ValueError(f"Invalid diastolic BP: {self.blood_pressure_diastolic}")
        
        # Validate heart rate
        if self.heart_rate is not None:
            if not 30 <= self.heart_rate <= 250:
                raise ValueError(f"Invalid heart rate: {self.heart_rate}")
        
        # Validate oxygen saturation
        if self.oxygen_saturation is not None:
            if not 50 <= self.oxygen_saturation <= 100:
                raise ValueError(f"Invalid oxygen saturation: {self.oxygen_saturation}")
    
    @property
    def bmi(self) -> Optional[float]:
        """Calculate BMI if height and weight available."""
        if self.weight and self.height:
            height_m = self.height / 100
            return round(self.weight / (height_m ** 2), 1)
        return None


@dataclass(frozen=True)
class RedFlag:
    """Red flag indicator value object."""
    
    condition: str
    severity: RedFlagSeverity
    detected_at: datetime
    context: str
    confidence: float = 1.0
    escalation_required: bool = False
    
    def __post_init__(self):
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"Invalid confidence: {self.confidence}")
        
        # Critical red flags always require escalation
        if self.severity == RedFlagSeverity.CRITICAL:
            object.__setattr__(self, 'escalation_required', True)


@dataclass(frozen=True)
class OrthopedicAssessment:
    """Orthopedic-specific assessment value object."""
    
    mechanism_of_injury: Optional[str] = None
    weight_bearing_status: Optional[bool] = None
    range_of_motion: Optional[str] = None
    swelling_present: Optional[bool] = None
    deformity_noted: Optional[bool] = None
    neurovascular_status: Optional[str] = None
    pain_location: Optional[str] = None
    pain_character: Optional[str] = None
    prior_injury: Optional[bool] = None
    prior_surgery: Optional[bool] = None
    
    def is_high_risk(self) -> bool:
        """Check if assessment indicates high risk."""
        high_risk_indicators = [
            self.deformity_noted,
            self.neurovascular_status and "compromised" in self.neurovascular_status.lower(),
            self.weight_bearing_status is False,
            self.mechanism_of_injury and any(
                term in self.mechanism_of_injury.lower()
                for term in ["fall from height", "mvc", "high energy", "crush"]
            )
        ]
        return any(high_risk_indicators)


@dataclass(frozen=True)
class ConversationTurn:
    """Single turn in conversation."""
    
    turn_id: int
    timestamp: datetime
    user_input: Dict[str, Any]
    ai_response: Dict[str, Any]
    language_detected: Optional[Language] = None
    safety_check: Optional[SafetyCheckResult] = None
    red_flags_detected: List[RedFlag] = None
    
    def __post_init__(self):
        if self.turn_id < 0:
            raise ValueError("Turn ID must be non-negative")
        if not self.user_input:
            raise ValueError("User input is required")
        if not self.ai_response:
            raise ValueError("AI response is required")


@dataclass(frozen=True)
class IntakeCompleteness:
    """Measure of intake completeness."""
    
    chief_complaint_collected: bool = False
    hpi_collected: bool = False
    pmh_collected: bool = False
    medications_collected: bool = False
    allergies_collected: bool = False
    social_history_collected: bool = False
    family_history_collected: bool = False
    ros_collected: bool = False
    
    @property
    def score(self) -> float:
        """Calculate completeness score (0-1)."""
        fields = [
            self.chief_complaint_collected,
            self.hpi_collected,
            self.pmh_collected,
            self.medications_collected,
            self.allergies_collected,
            self.social_history_collected,
            self.family_history_collected,
            self.ros_collected
        ]
        return sum(fields) / len(fields)
    
    @property
    def is_complete(self) -> bool:
        """Check if intake meets minimum requirements."""
        # Minimum: chief complaint, HPI, medications, allergies
        return all([
            self.chief_complaint_collected,
            self.hpi_collected,
            self.medications_collected,
            self.allergies_collected
        ])
    
    @property
    def missing_sections(self) -> List[str]:
        """Get list of missing sections."""
        sections = []
        if not self.chief_complaint_collected:
            sections.append("Chief Complaint")
        if not self.hpi_collected:
            sections.append("History of Present Illness")
        if not self.pmh_collected:
            sections.append("Past Medical History")
        if not self.medications_collected:
            sections.append("Medications")
        if not self.allergies_collected:
            sections.append("Allergies")
        if not self.social_history_collected:
            sections.append("Social History")
        if not self.family_history_collected:
            sections.append("Family History")
        if not self.ros_collected:
            sections.append("Review of Systems")
        return sections