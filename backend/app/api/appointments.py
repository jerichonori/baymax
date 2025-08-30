from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.models import Appointment, Patient, Provider
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
    AppointmentSlot,
)
from app.api.auth import get_current_user
from app.services.notification import NotificationService
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment_data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> AppointmentResponse:
    conflicts = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.provider_id == appointment_data.provider_id,
                Appointment.scheduled_at == appointment_data.scheduled_at,
                Appointment.status != "cancelled",
            )
        )
    )
    if conflicts.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Time slot already booked",
        )
    
    appointment = Appointment(**appointment_data.model_dump())
    
    if appointment.appointment_type == "virtual":
        pass
    
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    
    notification_service = NotificationService()
    patient_result = await db.execute(
        select(Patient).where(Patient.id == appointment.patient_id)
    )
    patient = patient_result.scalar_one()
    
    await notification_service.send_sms(
        phone=patient.phone,
        message=f"Appointment confirmed for {appointment.scheduled_at.strftime('%B %d at %I:%M %p')}",
    )
    
    return AppointmentResponse.model_validate(appointment)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> AppointmentResponse:
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    
    return AppointmentResponse.model_validate(appointment)


@router.put("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: UUID,
    appointment_data: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> AppointmentResponse:
    result = await db.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
    
    update_data = appointment_data.model_dump(exclude_unset=True)
    
    if "status" in update_data and update_data["status"] == "cancelled":
        appointment.cancelled_at = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(appointment, field, value)
    
    await db.commit()
    await db.refresh(appointment)
    
    return AppointmentResponse.model_validate(appointment)


@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    patient_id: Optional[UUID] = Query(None),
    provider_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> List[AppointmentResponse]:
    query = select(Appointment)
    
    if patient_id:
        query = query.where(Appointment.patient_id == patient_id)
    
    if provider_id:
        query = query.where(Appointment.provider_id == provider_id)
    
    if status:
        query = query.where(Appointment.status == status)
    
    if date_from:
        query = query.where(Appointment.scheduled_at >= date_from)
    
    if date_to:
        query = query.where(Appointment.scheduled_at <= date_to)
    
    query = query.order_by(Appointment.scheduled_at).limit(limit).offset(offset)
    result = await db.execute(query)
    appointments = result.scalars().all()
    
    return [AppointmentResponse.model_validate(a) for a in appointments]


@router.get("/slots/available", response_model=List[AppointmentSlot])
async def get_available_slots(
    provider_id: UUID,
    date: datetime,
    appointment_type: str = Query("physical", pattern="^(physical|virtual)$"),
    db: AsyncSession = Depends(get_db),
) -> List[AppointmentSlot]:
    start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    
    booked_result = await db.execute(
        select(Appointment).where(
            and_(
                Appointment.provider_id == provider_id,
                Appointment.scheduled_at >= start_date,
                Appointment.scheduled_at < end_date,
                Appointment.status != "cancelled",
            )
        )
    )
    booked_appointments = booked_result.scalars().all()
    booked_times = {a.scheduled_at for a in booked_appointments}
    
    slots = []
    current_time = start_date.replace(hour=9, minute=0)
    end_time = start_date.replace(hour=17, minute=0)
    
    while current_time < end_time:
        if current_time not in booked_times and current_time > datetime.utcnow():
            slots.append(
                AppointmentSlot(
                    provider_id=provider_id,
                    date=date,
                    start_time=current_time,
                    end_time=current_time + timedelta(minutes=settings.APPOINTMENT_SLOT_DURATION_MINUTES),
                    duration_minutes=settings.APPOINTMENT_SLOT_DURATION_MINUTES,
                    available=True,
                    appointment_type=appointment_type,
                )
            )
        current_time += timedelta(minutes=settings.APPOINTMENT_SLOT_DURATION_MINUTES + settings.APPOINTMENT_BUFFER_MINUTES)
    
    return slots