from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def log_event(
        self,
        actor_id: UUID,
        actor_type: str,
        action: str,
        resource_type: str,
        resource_id: UUID,
        ip_address: str,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        phi_accessed: bool = False,
        trace_id: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        try:
            audit_log = AuditLog(
                event_id=f"{action}_{resource_type}_{datetime.utcnow().timestamp()}",
                timestamp=datetime.utcnow(),
                actor_id=actor_id,
                actor_type=actor_type,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                details=details,
                error_message=error_message,
                phi_accessed=phi_accessed,
                trace_id=trace_id,
            )
            
            self.db.add(audit_log)
            await self.db.commit()
            
            logger.info(
                "Audit log created",
                event_id=audit_log.event_id,
                action=action,
                resource_type=resource_type,
                actor_id=str(actor_id),
            )
            
            return audit_log
            
        except Exception as e:
            logger.error(
                "Failed to create audit log",
                error=str(e),
                action=action,
                resource_type=resource_type,
            )
            raise
    
    async def log_phi_access(
        self,
        actor_id: UUID,
        actor_type: str,
        patient_id: UUID,
        action: str,
        ip_address: str,
        trace_id: Optional[str] = None,
    ) -> AuditLog:
        return await self.log_event(
            actor_id=actor_id,
            actor_type=actor_type,
            action=action,
            resource_type="patient",
            resource_id=patient_id,
            ip_address=ip_address,
            phi_accessed=True,
            trace_id=trace_id,
        )
    
    async def log_consent(
        self,
        patient_id: UUID,
        consent_type: str,
        consent_given: bool,
        ip_address: str,
        trace_id: Optional[str] = None,
    ) -> AuditLog:
        return await self.log_event(
            actor_id=patient_id,
            actor_type="patient",
            action="consent_recorded",
            resource_type="consent",
            resource_id=patient_id,
            ip_address=ip_address,
            details={
                "consent_type": consent_type,
                "consent_given": consent_given,
            },
            trace_id=trace_id,
        )