import pytest
from datetime import date, datetime
from pydantic import ValidationError

from app.schemas.patient import PatientCreate, PatientUpdate
from app.schemas.provider import ProviderCreate
from app.schemas.appointment import AppointmentCreate
from app.schemas.auth import OTPRequest, OTPVerify


class TestPatientSchemas:
    def test_patient_create_valid(self):
        patient_data = {
            "phone": "9876543210",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": date(1990, 1, 1),
            "gender": "male",
        }
        patient = PatientCreate(**patient_data)
        assert patient.phone == "9876543210"
        assert patient.email == "test@example.com"
    
    def test_patient_create_invalid_phone(self):
        patient_data = {
            "phone": "123",  # Too short
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": date(1990, 1, 1),
        }
        with pytest.raises(ValidationError) as exc_info:
            PatientCreate(**patient_data)
        assert "phone" in str(exc_info.value)
    
    def test_patient_create_invalid_dob(self):
        patient_data = {
            "phone": "9876543210",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": date(2030, 1, 1),  # Future date
        }
        with pytest.raises(ValidationError) as exc_info:
            PatientCreate(**patient_data)
        assert "future" in str(exc_info.value).lower()
    
    def test_patient_update_partial(self):
        update_data = {
            "email": "newemail@example.com",
        }
        patient_update = PatientUpdate(**update_data)
        assert patient_update.email == "newemail@example.com"
        assert patient_update.phone is None


class TestProviderSchemas:
    def test_provider_create_valid(self):
        provider_data = {
            "email": "doctor@example.com",
            "phone": "9876543210",
            "password": "Test@1234",
            "first_name": "Dr. John",
            "last_name": "Smith",
            "registration_number": "MED12345",
            "specialization": "orthopedics",
        }
        provider = ProviderCreate(**provider_data)
        assert provider.email == "doctor@example.com"
        assert provider.specialization == "orthopedics"
    
    def test_provider_create_weak_password(self):
        provider_data = {
            "email": "doctor@example.com",
            "phone": "9876543210",
            "password": "weak",  # Too weak
            "first_name": "Dr. John",
            "last_name": "Smith",
            "registration_number": "MED12345",
            "specialization": "orthopedics",
        }
        with pytest.raises(ValidationError) as exc_info:
            ProviderCreate(**provider_data)
        assert "password" in str(exc_info.value).lower()
    
    def test_provider_create_invalid_specialization(self):
        provider_data = {
            "email": "doctor@example.com",
            "phone": "9876543210",
            "password": "Test@1234",
            "first_name": "Dr. John",
            "last_name": "Smith",
            "registration_number": "MED12345",
            "specialization": "invalid",  # Invalid specialization
        }
        with pytest.raises(ValidationError) as exc_info:
            ProviderCreate(**provider_data)
        assert "specialization" in str(exc_info.value).lower()


class TestAppointmentSchemas:
    def test_appointment_create_valid(self):
        import uuid
        appointment_data = {
            "patient_id": str(uuid.uuid4()),
            "provider_id": str(uuid.uuid4()),
            "appointment_type": "physical",
            "scheduled_at": datetime.utcnow() + timedelta(days=1),
            "duration_minutes": 30,
        }
        appointment = AppointmentCreate(**appointment_data)
        assert appointment.appointment_type == "physical"
        assert appointment.duration_minutes == 30
    
    def test_appointment_create_past_date(self):
        import uuid
        from datetime import timedelta
        appointment_data = {
            "patient_id": str(uuid.uuid4()),
            "provider_id": str(uuid.uuid4()),
            "scheduled_at": datetime.utcnow() - timedelta(days=1),  # Past date
            "duration_minutes": 30,
        }
        with pytest.raises(ValidationError) as exc_info:
            AppointmentCreate(**appointment_data)
        assert "past" in str(exc_info.value).lower()
    
    def test_appointment_create_invalid_duration(self):
        import uuid
        from datetime import timedelta
        appointment_data = {
            "patient_id": str(uuid.uuid4()),
            "provider_id": str(uuid.uuid4()),
            "scheduled_at": datetime.utcnow() + timedelta(days=1),
            "duration_minutes": 200,  # Too long
        }
        with pytest.raises(ValidationError) as exc_info:
            AppointmentCreate(**appointment_data)
        assert "duration" in str(exc_info.value).lower()


class TestAuthSchemas:
    def test_otp_request_valid(self):
        otp_request = OTPRequest(phone="9876543210")
        assert otp_request.phone == "9876543210"
    
    def test_otp_request_invalid_phone(self):
        with pytest.raises(ValidationError) as exc_info:
            OTPRequest(phone="123")  # Too short
        assert "phone" in str(exc_info.value).lower()
    
    def test_otp_verify_valid(self):
        otp_verify = OTPVerify(phone="9876543210", otp="123456")
        assert otp_verify.phone == "9876543210"
        assert otp_verify.otp == "123456"
    
    def test_otp_verify_invalid_otp_length(self):
        with pytest.raises(ValidationError) as exc_info:
            OTPVerify(phone="9876543210", otp="12345")  # Too short
        assert "otp" in str(exc_info.value).lower()