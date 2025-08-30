from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_password_hash
from app.models import Provider
from app.schemas.provider import ProviderCreate, ProviderUpdate, ProviderResponse
from app.api.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=ProviderResponse)
async def create_provider(
    provider_data: ProviderCreate,
    db: AsyncSession = Depends(get_db),
) -> ProviderResponse:
    existing = await db.execute(
        select(Provider).where(
            (Provider.email == provider_data.email) |
            (Provider.registration_number == provider_data.registration_number)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider with this email or registration number already exists",
        )
    
    provider_dict = provider_data.model_dump()
    password = provider_dict.pop("password")
    provider = Provider(
        **provider_dict,
        hashed_password=get_password_hash(password)
    )
    
    db.add(provider)
    await db.commit()
    await db.refresh(provider)
    
    return ProviderResponse.model_validate(provider)


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ProviderResponse:
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found",
        )
    
    return ProviderResponse.model_validate(provider)


@router.put("/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: UUID,
    provider_data: ProviderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> ProviderResponse:
    if str(current_user["user_id"]) != str(provider_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only update your own profile",
        )
    
    result = await db.execute(select(Provider).where(Provider.id == provider_id))
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found",
        )
    
    update_data = provider_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(provider, field, value)
    
    await db.commit()
    await db.refresh(provider)
    
    return ProviderResponse.model_validate(provider)


@router.get("/", response_model=List[ProviderResponse])
async def list_providers(
    specialization: Optional[str] = Query(None),
    is_available: Optional[bool] = Query(None),
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> List[ProviderResponse]:
    query = select(Provider).where(Provider.is_active == True)
    
    if specialization:
        query = query.where(Provider.specialization == specialization)
    
    if is_available is not None:
        query = query.where(Provider.is_available == is_available)
    
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    providers = result.scalars().all()
    
    return [ProviderResponse.model_validate(p) for p in providers]