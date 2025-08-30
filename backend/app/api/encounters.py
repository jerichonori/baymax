from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models import Encounter
from app.schemas.encounter import EncounterCreate, EncounterUpdate, EncounterResponse
from app.api.auth import get_current_user
from app.services.audit import AuditService

router = APIRouter()


@router.post("/", response_model=EncounterResponse)
async def create_encounter(
    encounter_data: EncounterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> EncounterResponse:
    encounter = Encounter(**encounter_data.model_dump())
    
    db.add(encounter)
    await db.commit()
    await db.refresh(encounter)
    
    audit_service = AuditService(db)
    await audit_service.log_event(
        actor_id=current_user["user_id"],
        actor_type="provider",
        action="create",
        resource_type="encounter",
        resource_id=encounter.id,
        ip_address="127.0.0.1",
        phi_accessed=True,
    )
    
    return EncounterResponse.model_validate(encounter)


@router.get("/{encounter_id}", response_model=EncounterResponse)
async def get_encounter(
    encounter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> EncounterResponse:
    result = await db.execute(
        select(Encounter).where(Encounter.id == encounter_id)
    )
    encounter = result.scalar_one_or_none()
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found",
        )
    
    audit_service = AuditService(db)
    await audit_service.log_phi_access(
        actor_id=current_user["user_id"],
        actor_type="provider",
        patient_id=encounter.patient_id,
        action="read_encounter",
        ip_address="127.0.0.1",
    )
    
    return EncounterResponse.model_validate(encounter)


@router.put("/{encounter_id}", response_model=EncounterResponse)
async def update_encounter(
    encounter_id: UUID,
    encounter_data: EncounterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> EncounterResponse:
    result = await db.execute(
        select(Encounter).where(Encounter.id == encounter_id)
    )
    encounter = result.scalar_one_or_none()
    
    if not encounter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Encounter not found",
        )
    
    update_data = encounter_data.model_dump(exclude_unset=True)
    
    if "status" in update_data and update_data["status"] == "signed":
        from datetime import datetime
        encounter.signed_at = datetime.utcnow()
    
    encounter.version += 1
    
    for field, value in update_data.items():
        setattr(encounter, field, value)
    
    await db.commit()
    await db.refresh(encounter)
    
    audit_service = AuditService(db)
    await audit_service.log_event(
        actor_id=current_user["user_id"],
        actor_type="provider",
        action="update",
        resource_type="encounter",
        resource_id=encounter.id,
        ip_address="127.0.0.1",
        phi_accessed=True,
        details={"version": encounter.version},
    )
    
    return EncounterResponse.model_validate(encounter)


@router.get("/", response_model=List[EncounterResponse])
async def list_encounters(
    patient_id: Optional[UUID] = Query(None),
    provider_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[EncounterResponse]:
    query = select(Encounter)
    
    if patient_id:
        query = query.where(Encounter.patient_id == patient_id)
    
    if provider_id:
        query = query.where(Encounter.provider_id == provider_id)
    
    if status:
        query = query.where(Encounter.status == status)
    
    query = query.order_by(Encounter.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    encounters = result.scalars().all()
    
    return [EncounterResponse.model_validate(e) for e in encounters]