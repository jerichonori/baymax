import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta


@pytest.mark.asyncio
class TestAppointmentsAPI:
    async def test_create_appointment(
        self,
        client: AsyncClient,
        mock_auth_token,
        sample_patient,
        sample_provider,
    ):
        from unittest.mock import patch, AsyncMock
        
        appointment_data = {
            "patient_id": str(sample_patient.id),
            "provider_id": str(sample_provider.id),
            "appointment_type": "physical",
            "scheduled_at": (datetime.utcnow() + timedelta(days=2)).isoformat(),
            "duration_minutes": 30,
            "reason": "Regular checkup",
        }
        
        with patch("app.services.notification.NotificationService.send_sms") as mock_sms:
            mock_sms.return_value = True
            
            response = await client.post(
                "/api/v1/appointments/",
                json=appointment_data,
                headers={"Authorization": f"Bearer {mock_auth_token}"},
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["patient_id"] == appointment_data["patient_id"]
        assert data["provider_id"] == appointment_data["provider_id"]
        assert data["status"] == "scheduled"
        assert "id" in data
    
    async def test_create_appointment_conflict(
        self,
        client: AsyncClient,
        mock_auth_token,
        sample_appointment,
    ):
        # Try to book same slot
        appointment_data = {
            "patient_id": str(sample_appointment.patient_id),
            "provider_id": str(sample_appointment.provider_id),
            "appointment_type": "physical",
            "scheduled_at": sample_appointment.scheduled_at.isoformat(),
            "duration_minutes": 30,
        }
        
        response = await client.post(
            "/api/v1/appointments/",
            json=appointment_data,
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 409
        assert "already booked" in response.json()["detail"]
    
    async def test_get_appointment(
        self,
        client: AsyncClient,
        mock_auth_token,
        sample_appointment,
    ):
        response = await client.get(
            f"/api/v1/appointments/{sample_appointment.id}",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_appointment.id)
        assert data["status"] == sample_appointment.status
    
    async def test_update_appointment(
        self,
        client: AsyncClient,
        mock_auth_token,
        sample_appointment,
    ):
        update_data = {
            "status": "confirmed",
            "notes": "Patient confirmed attendance",
        }
        
        response = await client.put(
            f"/api/v1/appointments/{sample_appointment.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"
        assert data["notes"] == update_data["notes"]
    
    async def test_cancel_appointment(
        self,
        client: AsyncClient,
        mock_auth_token,
        sample_appointment,
    ):
        update_data = {
            "status": "cancelled",
            "cancellation_reason": "Patient requested cancellation",
        }
        
        response = await client.put(
            f"/api/v1/appointments/{sample_appointment.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
        assert data["cancellation_reason"] == update_data["cancellation_reason"]
        assert data["cancelled_at"] is not None
    
    async def test_list_appointments(
        self,
        client: AsyncClient,
        mock_auth_token,
        sample_appointment,
    ):
        response = await client.get(
            "/api/v1/appointments/",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(a["id"] == str(sample_appointment.id) for a in data)
    
    async def test_list_appointments_by_patient(
        self,
        client: AsyncClient,
        mock_auth_token,
        sample_appointment,
    ):
        response = await client.get(
            f"/api/v1/appointments/?patient_id={sample_appointment.patient_id}",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(a["patient_id"] == str(sample_appointment.patient_id) for a in data)
    
    async def test_list_appointments_by_provider(
        self,
        client: AsyncClient,
        mock_auth_token,
        sample_appointment,
    ):
        response = await client.get(
            f"/api/v1/appointments/?provider_id={sample_appointment.provider_id}",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert all(a["provider_id"] == str(sample_appointment.provider_id) for a in data)
    
    async def test_list_appointments_date_range(
        self,
        client: AsyncClient,
        mock_auth_token,
        sample_appointment,
    ):
        date_from = datetime.utcnow().isoformat()
        date_to = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        response = await client.get(
            f"/api/v1/appointments/?date_from={date_from}&date_to={date_to}",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        # All appointments should be within the date range
        for appointment in data:
            scheduled_at = datetime.fromisoformat(appointment["scheduled_at"].replace("Z", "+00:00"))
            assert scheduled_at >= datetime.fromisoformat(date_from)
            assert scheduled_at <= datetime.fromisoformat(date_to)
    
    async def test_get_available_slots(
        self,
        client: AsyncClient,
        mock_auth_token,
        sample_provider,
    ):
        tomorrow = datetime.utcnow() + timedelta(days=1)
        
        response = await client.get(
            f"/api/v1/appointments/slots/available"
            f"?provider_id={sample_provider.id}"
            f"&date={tomorrow.isoformat()}"
            f"&appointment_type=physical",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Should have slots available
        assert len(data) > 0
        
        # All slots should be available and in the future
        for slot in data:
            assert slot["available"] is True
            assert slot["provider_id"] == str(sample_provider.id)
            slot_time = datetime.fromisoformat(slot["start_time"].replace("Z", "+00:00"))
            assert slot_time > datetime.utcnow()