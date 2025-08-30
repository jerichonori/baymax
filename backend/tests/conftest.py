import asyncio
from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://baymax:baymax@localhost:5432/baymax_test"

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_auth_token():
    from app.core.security import create_access_token
    import uuid
    
    user_id = str(uuid.uuid4())
    token = create_access_token(subject=user_id, scopes=["provider"])
    return token


@pytest.fixture
def mock_patient_auth_token():
    from app.core.security import create_access_token
    import uuid
    
    patient_id = str(uuid.uuid4())
    token = create_access_token(subject=patient_id, scopes=["patient"])
    return token


@pytest.fixture
async def sample_patient(db_session: AsyncSession):
    from app.models import Patient
    from datetime import date
    
    patient = Patient(
        phone="9876543210",
        email="patient@example.com",
        first_name="Test",
        last_name="Patient",
        date_of_birth=date(1990, 1, 1),
        gender="male",
        language_preference="en",
    )
    db_session.add(patient)
    await db_session.commit()
    await db_session.refresh(patient)
    return patient


@pytest.fixture
async def sample_provider(db_session: AsyncSession):
    from app.models import Provider
    from app.core.security import get_password_hash
    
    provider = Provider(
        email="doctor@example.com",
        phone="9876543211",
        hashed_password=get_password_hash("Test@1234"),
        first_name="Dr. Test",
        last_name="Provider",
        registration_number="MED12345",
        specialization="orthopedics",
        is_active=True,
        is_verified=True,
    )
    db_session.add(provider)
    await db_session.commit()
    await db_session.refresh(provider)
    return provider


@pytest.fixture
async def sample_appointment(db_session: AsyncSession, sample_patient, sample_provider):
    from app.models import Appointment
    from datetime import datetime, timedelta
    
    appointment = Appointment(
        patient_id=sample_patient.id,
        provider_id=sample_provider.id,
        appointment_type="physical",
        scheduled_at=datetime.utcnow() + timedelta(days=1),
        duration_minutes=30,
        status="scheduled",
    )
    db_session.add(appointment)
    await db_session.commit()
    await db_session.refresh(appointment)
    return appointment