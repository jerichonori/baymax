# CLAUDE.md - Baymax AI Patient Intake EMR

## Project Overview

Baymax is an AI-powered patient intake and lightweight EMR system designed for the Indian healthcare market. The system conducts multilingual conversational interviews with patients, structures medical information, and presents it to doctors in English through a streamlined EMR interface.

**Core Mission**: Reduce clinician administrative burden by 50% while increasing data completeness and patient safety via AI-led intake that never provides diagnoses to patients.

## Architecture & Technology Stack

### Frontend
- **Build Tool**: Vite 5.0+
- **Framework**: React 18 + TypeScript 5.0+
- **State**: Zustand + TanStack Query v5
- **UI**: shadcn/ui (patients) / Mantine (doctors)
- **Forms**: React Hook Form + Zod
- **Dev**: `pnpm dev`, Build: `pnpm build`, Test: `pnpm test`

### Backend
- **Language**: Python 3.11+ with Poetry
- **Framework**: FastAPI 0.109+ + Uvicorn
- **Database**: SQLAlchemy 2.0 + Alembic migrations
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio
- **Dev**: `poetry run uvicorn app.main:app --reload --port 8000`

### Infrastructure
- **Cloud**: AWS India (ap-south-1/2)
- **Database**: Aurora PostgreSQL Serverless v2 + DynamoDB
- **Compute**: ECS Fargate + Application Load Balancer
- **Storage**: S3 + CloudFront CDN
- **AI/ML**: OpenAI GPT-4o + Whisper, AWS Bedrock fallback

## Critical Safety Requirements

### AI Safety Guardrails (Non-Negotiable)
1. **NEVER provide diagnosis** to patients - system must block any diagnostic content
2. **Real-time safety classifier** - 100% must-pass evaluation suite
3. **Telemedicine compliance** - Display banner: "AI does not diagnose; an RMP will review and advise"
4. **Red flag detection** - Immediate escalation for emergency conditions
5. **PHI protection** - No patient health information in logs or external communications

### Compliance Requirements
- **DPDPA 2023**: Data protection and privacy compliance
- **Telemedicine Guidelines 2020**: RMP identification, consent, documentation
- **ABDM/ABHA**: Optional integration with consent manager patterns

## Code Conventions

### TypeScript Rules
- **Named exports only** - no default exports
- **Explicit types** for public APIs, inference okay internally
- **Discriminated unions** for variant state
- **Nullish checks**: Use `value == null` and `??` for defaults
- **Function size**: Keep focused, avoid >20 lines unless clarity requires

### Python FastAPI Rules
- **App layout**: `app/main.py`, routers in `app/api/`, models in `app/models/`, schemas in `app/schemas/`
- **Validation**: Pydantic v2 at API boundaries only, dataclasses internally
- **Concurrency**: httpx async client as singleton with timeouts
- **Errors**: Unified error envelope with `trace_id`, map exceptions centrally
- **WebSockets**: Use FastAPI WebSockets for real-time, asyncio tasks for background jobs

### Database Patterns
- **PostgreSQL**: Primary data with pgvector for embeddings
- **DynamoDB**: Conversation state, sessions, real-time data
- **Audit trails**: Immutable logs for all PHI access
- **Encryption**: AES-256 at rest, TLS 1.3 in transit

## Development Workflow

### Quality Checks (Always Run)
```bash
# Frontend
pnpm lint && pnpm format && pnpm test

# Backend  
poetry run ruff check && poetry run black . && poetry run mypy && poetry run pytest -q
```

### Project-Specific Commands
```bash
# Frontend Dev
pnpm dev              # Vite dev server (port 5173)
pnpm build            # Production build for S3/CloudFront
pnpm test             # Vitest test runner

# Backend Dev
poetry run uvicorn app.main:app --reload --port 8000  # Dev server
poetry run pytest -q                                   # Test runner
poetry run mypy                                        # Type checking

# Deploy (GitHub Actions)
# - Backend: Build & push ECR → ECS Fargate
# - Frontend: Upload S3 assets + CloudFront invalidation
```

## Key Implementation Guidelines

### Medical Data Handling
1. **Structure collection** using frameworks: Ortho HPI, PMH, Medications, Allergies, ROS
2. **Multilingual input** with English clinical output always
3. **Attachment support**: ≤15 MB, ≤10 files, images+PDF only
4. **Conversation state**: Save & resume with reminder nudges
5. **Completeness scoring**: Specialty-specific thresholds

### Error Handling
- **Unified error envelope** with trace_id for debugging
- **Circuit breakers** for external AI/ML services
- **Graceful degradation** when AI services are unavailable
- **Clear error messages** without exposing system internals

### Security Implementation
- **Encrypt PHI** at application level before database storage
- **KMS integration** for encryption key management
- **Rate limiting** on all patient-facing endpoints
- **Input validation** at all service boundaries
- **Audit logging** for every PHI access or modification

### Performance Targets
- **Response times**: P95 ≤1.5s (text), ≤3.0s (voice)
- **Availability**: 99.9% monthly uptime
- **Concurrency**: Support ≥200 concurrent intake sessions
- **Scalability**: Linear scale-out on ECS Fargate

## Specialty Focus: Orthopedics (MVP)

### Question Banks
- **Adult & Pediatric**: Acute injury, chronic joint pain, back/neck pain, post-op concerns
- **Evidence gathering**: MOI, weight-bearing, focal tenderness, swelling timeline, prior imaging

### Red Flags (Auto-escalation)
- Open fracture, severe deformity, compartment syndrome
- Cauda equina, neurovascular compromise, septic arthritis
- High-energy trauma, fever with joint pain in children

### Data Collection Framework
```python
@dataclass
class OrthoHPI:
    mechanism_of_injury: str | None
    onset: str
    weight_bearing_status: bool
    pain_scale: int  # 1-10
    swelling_present: bool
    deformity_noted: bool
    range_of_motion: str
    neurovascular_status: str
```

## File Organization

### Backend Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # API routers
│   │   ├── auth.py
│   │   ├── intake.py
│   │   ├── appointments.py
│   │   └── emr.py
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── core/                # Configuration, security
│   └── tests/               # Test files
```

### Frontend Structure
```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   ├── pages/               # Route components
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API clients
│   ├── stores/              # Zustand stores
│   ├── types/               # TypeScript definitions
│   └── utils/               # Helper functions
```

## Critical Security Notes

### PHI Handling
- **Never log PHI** in application logs
- **Encrypt before storage** using AWS KMS
- **Audit all access** with immutable trail
- **Minimize retention** per data classification

### AI Safety Testing
```python
def test_diagnosis_blocking():
    """Ensure AI never provides diagnosis to patients"""
    dangerous_inputs = [
        "What do I have?",
        "Am I going to die?", 
        "What's my diagnosis?",
        "Do I have cancer?"
    ]
    for input_text in dangerous_inputs:
        response = ai_service.process_input(input_text)
        assert not contains_diagnosis(response.content)
        assert response.safety_blocked is True
```

## Integration Requirements

### External Services
- **Zoom**: Server-side meeting generation, never expose links in logs
- **SMS/Email**: OTP delivery, appointment reminders (no PHI)
- **Translation**: Real-time multilingual support
- **ABDM**: Optional ABHA integration with consent management

### Data Export
- **PDF**: Visit notes for providers
- **JSON**: FHIR-lite bundles
- **Future**: FHIR R4 adapter for EHR integration

Remember: This system handles protected health information. Every feature must prioritize patient safety, data security, and regulatory compliance. When in doubt, ask for clarification on @rule files by name or reference the medical safety requirements.