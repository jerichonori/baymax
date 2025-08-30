from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class AppointmentBase(BaseModel):
    patient_id: UUID
    provider_id: UUID
    appointment_type: str = Field(default="physical", pattern="^(physical|virtual)$")
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=15, le=120)
    reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    
    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_at(cls, v: datetime) -> datetime:
        if v < datetime.utcnow():
            raise ValueError("Appointment cannot be scheduled in the past")
        return v


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=120)
    status: Optional[str] = Field(None, pattern="^(scheduled|confirmed|cancelled|completed)$")
    reason: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=1000)
    cancellation_reason: Optional[str] = Field(None, max_length=500)


class AppointmentResponse(AppointmentBase):
    id: UUID
    status: str
    zoom_link: Optional[str] = None
    intake_completed: bool
    intake_link: Optional[str] = None
    reminder_sent: bool
    checked_in_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AppointmentSlot(BaseModel):
    provider_id: UUID
    date: datetime
    start_time: datetime
    end_time: datetime
    duration_minutes: int
    available: bool
    appointment_type: str = Field(pattern="^(physical|virtual|both)$")