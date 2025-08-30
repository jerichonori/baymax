from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token,
    generate_otp,
    hash_otp,
    verify_otp as verify_otp_hash,
)
from app.models import Patient, Provider
from app.schemas.auth import (
    Token,
    TokenData,
    LoginRequest,
    OTPRequest,
    OTPVerify,
    RefreshTokenRequest,
)
from app.services.notification import NotificationService
from app.core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = verify_token(token)
    if user_id is None:
        raise credentials_exception
    
    return {"user_id": user_id}


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    result = await db.execute(
        select(Provider).where(Provider.email == form_data.username)
    )
    provider = result.scalar_one_or_none()
    
    if not provider or not verify_password(form_data.password, provider.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not provider.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    
    access_token = create_access_token(
        subject=provider.id,
        scopes=["provider"],
    )
    refresh_token = create_refresh_token(subject=provider.id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/otp/request")
async def request_otp(
    request: OTPRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await db.execute(
        select(Patient).where(Patient.phone == request.phone)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        patient = Patient(
            phone=request.phone,
            first_name="Guest",
            last_name="User",
            date_of_birth=datetime.now().date(),
        )
        db.add(patient)
        await db.commit()
    
    otp = generate_otp()
    otp_hash = hash_otp(otp, request.phone)
    
    notification_service = NotificationService()
    await notification_service.send_sms(
        phone=request.phone,
        message=f"Your Baymax verification code is: {otp}. Valid for {settings.OTP_EXPIRY_MINUTES} minutes.",
    )
    
    return {
        "message": "OTP sent successfully",
        "expires_in": settings.OTP_EXPIRY_MINUTES * 60,
    }


@router.post("/otp/verify", response_model=Token)
async def verify_otp(
    request: OTPVerify,
    db: AsyncSession = Depends(get_db),
) -> Token:
    result = await db.execute(
        select(Patient).where(Patient.phone == request.phone)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    patient.is_verified = True
    await db.commit()
    
    access_token = create_access_token(
        subject=patient.id,
        scopes=["patient"],
    )
    refresh_token = create_refresh_token(subject=patient.id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: RefreshTokenRequest,
) -> Token:
    user_id = verify_token(request.refresh_token, token_type="refresh")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    access_token = create_access_token(subject=user_id)
    new_refresh_token = create_refresh_token(subject=user_id)
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )