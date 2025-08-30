from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field


class ConversationType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"


class SafetyLevel(str, Enum):
    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"


class RedFlagSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConversationTurn(BaseModel):
    turn_id: int
    timestamp: datetime
    user_input: Dict[str, Any]
    ai_response: Dict[str, Any]
    language_detected: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    safety_check: Optional[SafetyLevel] = None


class RedFlag(BaseModel):
    condition: str
    severity: RedFlagSeverity
    detected_at: datetime
    context: str
    escalation_triggered: bool = False
    notification_sent: bool = False


class IntakeSession(BaseModel):
    session_id: UUID
    patient_id: UUID
    appointment_id: Optional[UUID] = None
    conversation_type: ConversationType
    conversation_turns: List[ConversationTurn] = []
    collected_data: Dict[str, Any] = {}
    red_flags: List[RedFlag] = []
    session_status: str = Field(pattern="^(active|paused|completed|escalated|abandoned)$")
    started_at: datetime
    last_activity_at: datetime
    completed_at: Optional[datetime] = None
    completion_score: Optional[float] = Field(None, ge=0, le=1)
    languages_used: List[str] = []


class IntakeCompletion(BaseModel):
    session_id: UUID
    completed: bool
    completion_score: float = Field(ge=0, le=1)
    total_turns: int
    duration_minutes: int
    chief_complaint: str
    hpi_collected: bool
    pmh_collected: bool
    medications_collected: bool
    allergies_collected: bool
    ros_collected: bool
    red_flags_detected: List[RedFlag] = []
    summary: Dict[str, Any]


class WebSocketMessage(BaseModel):
    type: str
    data: Any
    sequence: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AudioChunk(BaseModel):
    type: str = "audio_chunk"
    data: str  # base64 encoded audio
    sequence: int
    format: str = "webm"
    sample_rate: int = 16000


class TextMessage(BaseModel):
    type: str = "text_message"
    content: str
    language: Optional[str] = None


class AIResponse(BaseModel):
    type: str = "ai_response"
    content: str
    language: str
    confidence: float = Field(ge=0, le=1)
    follow_up_questions: Optional[List[str]] = None
    data_collected: Optional[Dict[str, Any]] = None


class RedFlagAlert(BaseModel):
    type: str = "red_flag_alert"
    message: str
    severity: RedFlagSeverity
    escalation_triggered: bool
    emergency_guidance: Optional[str] = None