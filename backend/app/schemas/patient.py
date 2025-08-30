from datetime import date, datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class PatientBase(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    abha_number: Optional[str] = Field(None, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    address: Optional[Dict[str, Any]] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    language_preference: str = Field(default="en", pattern="^[a-z]{2}$")
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        phone_regex = r"^[+]?[0-9]{10,15}$"
        if not re.match(phone_regex, v):
            raise ValueError("Invalid phone number format")
        return v
    
    @field_validator("date_of_birth")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        age = (date.today() - v).days / 365.25
        if age > 150:
            raise ValueError("Invalid date of birth")
        return v


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    email: Optional[EmailStr] = None
    abha_number: Optional[str] = Field(None, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    address: Optional[Dict[str, Any]] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    language_preference: Optional[str] = Field(None, pattern="^[a-z]{2}$")


class PatientResponse(PatientBase):
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PatientInDB(PatientResponse):
    pass