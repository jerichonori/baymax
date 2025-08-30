from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class ProviderBase(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    registration_number: str = Field(..., min_length=1, max_length=50)
    specialization: str = Field(..., min_length=1, max_length=100)
    qualifications: Optional[List[str]] = None
    working_hours: Optional[Dict[str, Any]] = None
    consultation_fee: Optional[int] = Field(None, ge=0)
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        phone_regex = r"^[+]?[0-9]{10,15}$"
        if not re.match(phone_regex, v):
            raise ValueError("Invalid phone number format")
        return v
    
    @field_validator("specialization")
    @classmethod
    def validate_specialization(cls, v: str) -> str:
        allowed_specializations = ["orthopedics", "general", "cardiology", "pediatrics"]
        if v.lower() not in allowed_specializations:
            raise ValueError(f"Specialization must be one of {allowed_specializations}")
        return v.lower()


class ProviderCreate(ProviderBase):
    password: str = Field(..., min_length=8)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class ProviderUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    qualifications: Optional[List[str]] = None
    working_hours: Optional[Dict[str, Any]] = None
    consultation_fee: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None


class ProviderResponse(ProviderBase):
    id: UUID
    is_active: bool
    is_verified: bool
    is_available: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProviderInDB(ProviderResponse):
    hashed_password: str