from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
import openai

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.intake import IntakeSession, IntakeCompletion, RedFlag

logger = get_logger(__name__)


class AIIntakeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.sessions: Dict[str, IntakeSession] = {}
    
    async def create_session(
        self,
        session_id: str,
        appointment_id: UUID,
    ) -> IntakeSession:
        session = IntakeSession(
            session_id=UUID(session_id),
            patient_id=UUID("00000000-0000-0000-0000-000000000000"),  
            appointment_id=appointment_id,
            conversation_type="text",
            session_status="active",
            started_at=datetime.utcnow(),
            last_activity_at=datetime.utcnow(),
        )
        
        self.sessions[session_id] = session
        
        logger.info(f"Created intake session {session_id}")
        
        return session
    
    async def process_text_input(
        self,
        session_id: str,
        text: str,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            return {
                "type": "error",
                "message": "Session not found",
            }
        
        safety_check = await self._check_safety(text)
        if safety_check == "blocked":
            return {
                "type": "ai_response",
                "content": "I'm here to help gather your medical information. Could you please describe your symptoms or concerns?",
                "language": language or "en",
                "confidence": 1.0,
            }
        
        red_flags = await self._detect_red_flags(text)
        if red_flags:
            session.red_flags.extend(red_flags)
            return {
                "type": "red_flag_alert",
                "message": "Please seek immediate medical attention",
                "severity": red_flags[0].severity,
                "escalation_triggered": True,
            }
        
        response = await self._generate_response(text, session)
        
        session.last_activity_at = datetime.utcnow()
        
        return {
            "type": "ai_response",
            "content": response,
            "language": language or "en",
            "confidence": 0.95,
        }
    
    async def _check_safety(self, text: str) -> str:
        dangerous_patterns = [
            "what's my diagnosis",
            "am i going to die",
            "what disease do i have",
            "prescribe medication",
            "do i have cancer",
            "what medication",
            "diagnosis",
        ]
        
        text_lower = text.lower()
        for pattern in dangerous_patterns:
            if pattern in text_lower:
                return "blocked"
        
        return "safe"
    
    async def _detect_red_flags(self, text: str) -> list[RedFlag]:
        red_flag_patterns = {
            "can't feel my legs": ("critical", "Possible cauda equina syndrome"),
            "severe chest pain": ("critical", "Possible cardiac emergency"),
            "difficulty breathing": ("critical", "Respiratory distress"),
            "severe bleeding": ("critical", "Hemorrhage"),
        }
        
        text_lower = text.lower()
        red_flags = []
        
        for pattern, (severity, condition) in red_flag_patterns.items():
            if pattern in text_lower:
                red_flags.append(
                    RedFlag(
                        condition=condition,
                        severity=severity,
                        detected_at=datetime.utcnow(),
                        context=text,
                        escalation_triggered=True,
                    )
                )
        
        return red_flags
    
    async def _generate_response(self, text: str, session: IntakeSession) -> str:
        try:
            system_prompt = """You are a medical intake assistant. Your role is to:
            1. Gather medical information from patients
            2. Never provide diagnosis or medical advice
            3. Ask relevant follow-up questions
            4. Be empathetic and professional
            5. If asked for diagnosis, redirect to information gathering
            """
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=200,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to generate AI response: {str(e)}")
            return "I understand. Could you tell me more about your symptoms?"
    
    async def complete_session(self, session_id: str) -> IntakeCompletion:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")
        
        session.completed_at = datetime.utcnow()
        session.session_status = "completed"
        
        completion = IntakeCompletion(
            session_id=session.session_id,
            completed=True,
            completion_score=0.8,
            total_turns=len(session.conversation_turns),
            duration_minutes=int(
                (session.completed_at - session.started_at).total_seconds() / 60
            ),
            chief_complaint="Patient reported symptoms",
            hpi_collected=True,
            pmh_collected=False,
            medications_collected=False,
            allergies_collected=False,
            ros_collected=False,
            red_flags_detected=session.red_flags,
            summary={"status": "completed"},
        )
        
        return completion
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session_id,
            "status": session.session_status,
            "started_at": session.started_at.isoformat(),
            "last_activity_at": session.last_activity_at.isoformat(),
            "total_turns": len(session.conversation_turns),
            "red_flags_count": len(session.red_flags),
        }
    
    async def escalate_red_flag(
        self,
        session_id: str,
        red_flag: Dict[str, Any],
    ) -> None:
        logger.critical(
            f"Red flag escalation for session {session_id}",
            red_flag=red_flag,
        )