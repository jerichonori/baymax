from fastapi import APIRouter

from app.api import auth, patients, providers, appointments, encounters, intake, health

router = APIRouter()

router.include_router(health.router, tags=["health"])
router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(patients.router, prefix="/patients", tags=["patients"])
router.include_router(providers.router, prefix="/providers", tags=["providers"])
router.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
router.include_router(encounters.router, prefix="/encounters", tags=["encounters"])
router.include_router(intake.router, prefix="/intake", tags=["intake"])