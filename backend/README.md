# Baymax Backend - AI Patient Intake EMR System

## Overview

FastAPI-based backend for an AI-powered patient intake and lightweight EMR system designed for the Indian healthcare market. The system conducts multilingual conversational interviews with patients, structures medical information, and presents it to doctors in English.

## Tech Stack

- **Framework**: FastAPI 0.109+ with Python 3.11+
- **Database**: PostgreSQL 15 with SQLAlchemy 2.0
- **Cache**: Redis 7
- **AI/ML**: OpenAI GPT-4, Whisper API
- **Cloud**: AWS (S3, DynamoDB, SES, SNS)
- **Authentication**: JWT with OTP verification
- **WebSockets**: Real-time patient intake chat

## Features

- ✅ Multilingual patient intake with AI safety guardrails
- ✅ Real-time WebSocket communication for chat/voice
- ✅ Orthopedics specialty support with red flag detection
- ✅ Appointment scheduling with Zoom integration
- ✅ PHI encryption and DPDPA 2023 compliance
- ✅ Comprehensive audit logging
- ✅ OTP-based patient authentication
- ✅ Provider dashboard and EMR interface

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry
│   ├── api/                 # API routers
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── patients.py      # Patient management
│   │   ├── providers.py     # Provider management
│   │   ├── appointments.py  # Appointment scheduling
│   │   ├── encounters.py    # Clinical encounters
│   │   └── intake.py        # AI intake with WebSocket
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings management
│   │   ├── database.py      # Database connection
│   │   ├── security.py      # Security utilities
│   │   └── logging.py       # Structured logging
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic services
│   └── middleware/          # Custom middleware
├── tests/                   # Test files
├── alembic/                 # Database migrations
├── docker-compose.yml       # Local development setup
├── Dockerfile              # Container configuration
├── pyproject.toml          # Poetry dependencies
└── .env.example            # Environment variables template
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15
- Redis 7
- Docker & Docker Compose (optional)

### Installation

1. Clone the repository:
```bash
cd backend
```

2. Install dependencies with Poetry:
```bash
pip install poetry
poetry install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start services with Docker Compose:
```bash
docker-compose up -d postgres redis localstack
```

5. Run database migrations:
```bash
poetry run alembic upgrade head
```

6. Start the development server:
```bash
poetry run uvicorn app.main:app --reload --port 8000
```

### Using Docker

Run the entire stack with Docker Compose:
```bash
docker-compose up
```

## API Documentation

Once running, access the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Endpoints

### Authentication
- `POST /api/v1/auth/login` - Provider login
- `POST /api/v1/auth/otp/request` - Request OTP for patient
- `POST /api/v1/auth/otp/verify` - Verify OTP

### Patient Management
- `POST /api/v1/patients` - Create patient
- `GET /api/v1/patients/{id}` - Get patient details
- `GET /api/v1/patients` - Search patients

### Appointments
- `POST /api/v1/appointments` - Book appointment
- `GET /api/v1/appointments/slots/available` - Get available slots
- `PUT /api/v1/appointments/{id}` - Update appointment

### AI Intake
- `POST /api/v1/intake/sessions/{appointment_id}/start` - Start intake session
- `WS /api/v1/intake/ws/{session_id}` - WebSocket for real-time intake

### Encounters
- `POST /api/v1/encounters` - Create encounter
- `GET /api/v1/encounters/{id}` - Get encounter details
- `PUT /api/v1/encounters/{id}` - Update encounter

## Testing

Run tests with pytest:
```bash
poetry run pytest
poetry run pytest --cov=app --cov-report=html
```

## Code Quality

Run linting and formatting:
```bash
poetry run ruff check .
poetry run black .
poetry run mypy app
```

## Environment Variables

Key environment variables (see `.env.example` for full list):

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `SECRET_KEY` - JWT secret key
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `AWS_SECRET_ACCESS_KEY` - AWS credentials

## Security Features

- JWT-based authentication with refresh tokens
- OTP verification for patient access
- PHI encryption at rest and in transit
- Comprehensive audit logging
- Rate limiting and DDoS protection
- CORS and security headers middleware
- Input validation with Pydantic

## Compliance

- DPDPA 2023 (India Data Protection Act)
- Telemedicine Guidelines 2020
- ABDM/ABHA integration ready
- PHI handling with encryption
- Consent management system

## Development

### Database Migrations

Create a new migration:
```bash
poetry run alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
poetry run alembic upgrade head
```

### Adding New Features

1. Create model in `app/models/`
2. Create schemas in `app/schemas/`
3. Add service logic in `app/services/`
4. Create API router in `app/api/`
5. Include router in `app/api/__init__.py`
6. Write tests in `tests/`

## Production Deployment

For production deployment on AWS:

1. Build Docker image:
```bash
docker build -t baymax-backend .
```

2. Push to ECR:
```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin [ECR_URI]
docker tag baymax-backend:latest [ECR_URI]/baymax-backend:latest
docker push [ECR_URI]/baymax-backend:latest
```

3. Deploy with ECS Fargate or Kubernetes

## Support

For issues or questions, please refer to the project documentation or create an issue in the repository.

## License

Proprietary - Baymax Health