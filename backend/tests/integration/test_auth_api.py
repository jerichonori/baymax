import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.core.security import get_password_hash


@pytest.mark.asyncio
class TestAuthAPI:
    async def test_provider_login_success(self, client: AsyncClient, sample_provider):
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": sample_provider.email,
                "password": "Test@1234",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_provider_login_wrong_password(self, client: AsyncClient, sample_provider):
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": sample_provider.email,
                "password": "WrongPassword",
            },
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    async def test_provider_login_nonexistent_user(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "Test@1234",
            },
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    async def test_provider_login_inactive_account(self, client: AsyncClient, db_session):
        from app.models import Provider
        
        # Create inactive provider
        provider = Provider(
            email="inactive@example.com",
            phone="9876543212",
            hashed_password=get_password_hash("Test@1234"),
            first_name="Inactive",
            last_name="Provider",
            registration_number="MED99999",
            specialization="orthopedics",
            is_active=False,  # Inactive
        )
        db_session.add(provider)
        await db_session.commit()
        
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "inactive@example.com",
                "password": "Test@1234",
            },
        )
        
        assert response.status_code == 403
        assert "Account is inactive" in response.json()["detail"]
    
    @patch("app.services.notification.NotificationService.send_sms")
    async def test_otp_request_existing_patient(
        self,
        mock_send_sms: AsyncMock,
        client: AsyncClient,
        sample_patient,
    ):
        mock_send_sms.return_value = True
        
        response = await client.post(
            "/api/v1/auth/otp/request",
            json={"phone": sample_patient.phone},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "OTP sent successfully"
        assert "expires_in" in data
        
        mock_send_sms.assert_called_once()
    
    @patch("app.services.notification.NotificationService.send_sms")
    async def test_otp_request_new_patient(
        self,
        mock_send_sms: AsyncMock,
        client: AsyncClient,
        db_session,
    ):
        mock_send_sms.return_value = True
        
        response = await client.post(
            "/api/v1/auth/otp/request",
            json={"phone": "9999999999"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "OTP sent successfully"
        
        # Check if patient was created
        from sqlalchemy import select
        from app.models import Patient
        
        result = await db_session.execute(
            select(Patient).where(Patient.phone == "9999999999")
        )
        patient = result.scalar_one_or_none()
        assert patient is not None
        assert patient.first_name == "Guest"
    
    @patch("app.api.auth.verify_otp_hash")
    async def test_otp_verify_success(
        self,
        mock_verify_otp: AsyncMock,
        client: AsyncClient,
        sample_patient,
    ):
        mock_verify_otp.return_value = True
        
        response = await client.post(
            "/api/v1/auth/otp/verify",
            json={
                "phone": sample_patient.phone,
                "otp": "123456",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_otp_verify_nonexistent_patient(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/otp/verify",
            json={
                "phone": "0000000000",
                "otp": "123456",
            },
        )
        
        assert response.status_code == 404
        assert "Patient not found" in response.json()["detail"]
    
    async def test_refresh_token_success(self, client: AsyncClient):
        from app.core.security import create_refresh_token
        import uuid
        
        user_id = str(uuid.uuid4())
        refresh_token = create_refresh_token(subject=user_id)
        
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_refresh_token_invalid(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]