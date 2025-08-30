from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    user_type: Optional[str] = None
    scopes: list[str] = []


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class OTPRequest(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)


class OTPVerify(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    otp: str = Field(..., min_length=6, max_length=6)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class ConsentRequest(BaseModel):
    consent_type: str
    consent_given: bool
    consent_text: str
    version: str
    scope: Optional[dict] = None
    expires_at: Optional[datetime] = None