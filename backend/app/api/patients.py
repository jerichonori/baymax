from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.database import get_db
from app.models import Patient
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.api.auth import get_current_user
from app.services.audit import AuditService

router = APIRouter()


@router.post("/", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PatientResponse:
    existing = await db.execute(
        select(Patient).where(Patient.phone == patient_data.phone)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient with this phone number already exists",
        )
    
    patient = Patient(**patient_data.model_dump())
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    
    audit_service = AuditService(db)
    await audit_service.log_event(
        actor_id=current_user["user_id"],
        actor_type="provider",
        action="create",
        resource_type="patient",
        resource_id=patient.id,
        ip_address="127.0.0.1",
        phi_accessed=True,
    )
    
    return PatientResponse.model_validate(patient)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PatientResponse:
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    audit_service = AuditService(db)
    await audit_service.log_phi_access(
        actor_id=current_user["user_id"],
        actor_type="provider",
        patient_id=patient.id,
        action="read",
        ip_address="127.0.0.1",
    )
    
    return PatientResponse.model_validate(patient)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: UUID,
    patient_data: PatientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PatientResponse:
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
    
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    await db.commit()
    await db.refresh(patient)
    
    audit_service = AuditService(db)
    await audit_service.log_event(
        actor_id=current_user["user_id"],
        actor_type="provider",
        action="update",
        resource_type="patient",
        resource_id=patient.id,
        ip_address="127.0.0.1",
        phi_accessed=True,
    )
    
    return PatientResponse.model_validate(patient)


@router.get("/", response_model=List[PatientResponse])
async def search_patients(
    q: Optional[str] = Query(None, description="Search query"),
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[PatientResponse]:
    query = select(Patient)
    
    if q:
        search_filter = or_(
            Patient.first_name.ilike(f"%{q}%"),
            Patient.last_name.ilike(f"%{q}%"),
            Patient.phone.ilike(f"%{q}%"),
            Patient.email.ilike(f"%{q}%"),
            Patient.abha_number.ilike(f"%{q}%"),
        )
        query = query.where(search_filter)
    
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    patients = result.scalars().all()
    
    return [PatientResponse.model_validate(p) for p in patients]