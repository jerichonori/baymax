from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class HistoryPresentIllness(BaseModel):
    mechanism_of_injury: Optional[str] = None
    onset: Optional[str] = None
    weight_bearing_status: Optional[bool] = None
    pain_scale: Optional[int] = Field(None, ge=0, le=10)
    swelling_present: Optional[bool] = None
    deformity_noted: Optional[bool] = None
    range_of_motion: Optional[str] = None
    neurovascular_status: Optional[str] = None
    additional_notes: Optional[str] = None


class Medication(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    prescribed_by: Optional[str] = None


class Allergy(BaseModel):
    allergen: str
    reaction: str
    severity: str = Field(pattern="^(mild|moderate|severe)$")
    onset_date: Optional[datetime] = None


class ReviewOfSystems(BaseModel):
    constitutional: Optional[Dict[str, Any]] = None
    cardiovascular: Optional[Dict[str, Any]] = None
    respiratory: Optional[Dict[str, Any]] = None
    gastrointestinal: Optional[Dict[str, Any]] = None
    musculoskeletal: Optional[Dict[str, Any]] = None
    neurological: Optional[Dict[str, Any]] = None
    skin: Optional[Dict[str, Any]] = None
    psychiatric: Optional[Dict[str, Any]] = None


class IntakeSummary(BaseModel):
    chief_complaint: str
    hpi: Optional[HistoryPresentIllness] = None
    pmh: Optional[Dict[str, Any]] = None
    medications: Optional[List[Medication]] = None
    allergies: Optional[List[Allergy]] = None
    ros: Optional[ReviewOfSystems] = None
    red_flags: Optional[List[str]] = None
    ai_confidence: Optional[float] = Field(None, ge=0, le=1)
    languages_detected: Optional[List[str]] = None


class EncounterBase(BaseModel):
    patient_id: UUID
    provider_id: UUID
    appointment_id: Optional[UUID] = None
    intake_data: Optional[IntakeSummary] = None
    clinical_notes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None


class EncounterCreate(EncounterBase):
    pass


class EncounterUpdate(BaseModel):
    intake_data: Optional[IntakeSummary] = None
    clinical_notes: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|in_progress|completed|signed)$")


class EncounterResponse(EncounterBase):
    id: UUID
    status: str
    signed_at: Optional[datetime] = None
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True