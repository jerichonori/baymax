import factory
from factory import Factory, Faker, SubFactory, LazyFunction
from datetime import datetime, date, timedelta
import uuid

from app.models import Patient, Provider, Appointment, Encounter
from app.core.security import get_password_hash


class PatientFactory(Factory):
    class Meta:
        model = Patient
    
    id = LazyFunction(uuid.uuid4)
    phone = Faker("numerify", text="##########")
    email = Faker("email")
    abha_number = Faker("numerify", text="ABHA########")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    date_of_birth = Faker("date_of_birth", minimum_age=18, maximum_age=80)
    gender = Faker("random_element", elements=["male", "female", "other"])
    language_preference = Faker("random_element", elements=["en", "hi", "te", "ta"])
    is_active = True
    is_verified = False
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)


class ProviderFactory(Factory):
    class Meta:
        model = Provider
    
    id = LazyFunction(uuid.uuid4)
    email = Faker("email")
    phone = Faker("numerify", text="##########")
    hashed_password = LazyFunction(lambda: get_password_hash("Test@1234"))
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    registration_number = Faker("bothify", text="MED#####")
    specialization = Faker("random_element", elements=["orthopedics", "general", "cardiology"])
    is_active = True
    is_verified = True
    is_available = True
    consultation_fee = Faker("random_int", min=500, max=2000)
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)


class AppointmentFactory(Factory):
    class Meta:
        model = Appointment
    
    id = LazyFunction(uuid.uuid4)
    patient_id = LazyFunction(uuid.uuid4)
    provider_id = LazyFunction(uuid.uuid4)
    appointment_type = Faker("random_element", elements=["physical", "virtual"])
    scheduled_at = LazyFunction(lambda: datetime.utcnow() + timedelta(days=1))
    duration_minutes = 30
    status = "scheduled"
    reason = Faker("sentence")
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)


class EncounterFactory(Factory):
    class Meta:
        model = Encounter
    
    id = LazyFunction(uuid.uuid4)
    patient_id = LazyFunction(uuid.uuid4)
    provider_id = LazyFunction(uuid.uuid4)
    appointment_id = LazyFunction(uuid.uuid4)
    chief_complaint = Faker("sentence")
    status = "draft"
    version = 1
    created_at = LazyFunction(datetime.utcnow)
    updated_at = LazyFunction(datetime.utcnow)