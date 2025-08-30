from typing import Any, List, Optional, Union
from pydantic import AnyHttpUrl, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict
import secrets


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    PROJECT_NAME: str = "Baymax AI Patient Intake EMR"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    PRODUCTION: bool = False
    DEBUG: bool = True
    
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    ALGORITHM: str = "HS256"
    
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    ALLOWED_HOSTS: List[str] = ["*"]
    
    DATABASE_URL: Optional[str] = None
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "baymax"
    POSTGRES_PASSWORD: str = "baymax"
    POSTGRES_DB: str = "baymax"
    POSTGRES_PORT: int = 5432
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        values = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=values.get("POSTGRES_DB"),
        ).unicode_string()
    
    REDIS_URL: str = "redis://localhost:6379/0"
    
    AWS_REGION: str = "ap-south-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    
    S3_BUCKET_NAME: str = "baymax-patient-data"
    
    DYNAMODB_CONVERSATIONS_TABLE: str = "baymax-conversations"
    DYNAMODB_SESSIONS_TABLE: str = "baymax-sessions"
    DYNAMODB_APPOINTMENTS_TABLE: str = "baymax-appointments"
    DYNAMODB_AUDIT_TABLE: str = "baymax-audit"
    
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    
    AWS_BEDROCK_ENABLED: bool = False
    AWS_BEDROCK_MODEL: str = "anthropic.claude-instant-v1"
    
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    AWS_SES_REGION: str = "ap-south-1"
    AWS_SES_FROM_EMAIL: str = "noreply@baymax.health"
    
    ZOOM_API_KEY: Optional[str] = None
    ZOOM_API_SECRET: Optional[str] = None
    
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    
    PROMETHEUS_ENABLED: bool = True
    
    MAX_FILE_SIZE_MB: int = 15
    MAX_FILES_PER_UPLOAD: int = 10
    ALLOWED_FILE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".pdf"]
    
    INTAKE_MAX_TURNS: int = 50
    INTAKE_TIMEOUT_MINUTES: int = 30
    
    RED_FLAG_ESCALATION_ENABLED: bool = True
    RED_FLAG_NOTIFICATION_CHANNELS: List[str] = ["sms", "email", "system"]
    
    ENCRYPTION_KEY: Optional[str] = None
    
    PHI_RETENTION_DAYS: int = 2555  # 7 years as per Indian regulations
    AUDIT_LOG_RETENTION_DAYS: int = 2555
    
    SESSION_COOKIE_NAME: str = "baymax_session"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "strict"
    
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    LANGUAGE_DETECTION_ENABLED: bool = True
    SUPPORTED_LANGUAGES: List[str] = ["en", "hi", "te", "ta", "bn", "mr", "gu", "kn", "ml", "pa", "ur"]
    
    SPECIALTIES_ENABLED: List[str] = ["orthopedics"]
    
    TELEMEDICINE_BANNER_TEXT: str = "AI does not diagnose; an RMP will review and advise"
    
    DPDPA_COMPLIANCE_ENABLED: bool = True
    ABDM_INTEGRATION_ENABLED: bool = False
    
    AUDIT_EVENTS_ENABLED: bool = True
    
    MIN_PASSWORD_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_NUMBERS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    OTP_LENGTH: int = 6
    OTP_EXPIRY_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 3
    
    APPOINTMENT_SLOT_DURATION_MINUTES: int = 30
    APPOINTMENT_BUFFER_MINUTES: int = 5
    APPOINTMENT_ADVANCE_BOOKING_DAYS: int = 30
    
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    WEBSOCKET_CONNECTION_TIMEOUT: int = 60


settings = Settings()