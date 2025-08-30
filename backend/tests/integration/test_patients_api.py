import pytest
from httpx import AsyncClient
from datetime import date


@pytest.mark.asyncio
class TestPatientsAPI:
    async def test_create_patient(self, client: AsyncClient, mock_auth_token):
        patient_data = {
            "phone": "9876543999",
            "email": "newpatient@example.com",
            "first_name": "New",
            "last_name": "Patient",
            "date_of_birth": "1990-01-01",
            "gender": "female",
        }
        
        response = await client.post(
            "/api/v1/patients/",
            json=patient_data,
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == patient_data["phone"]
        assert data["email"] == patient_data["email"]
        assert data["first_name"] == patient_data["first_name"]
        assert "id" in data
    
    async def test_create_patient_duplicate_phone(
        self,
        client: AsyncClient,
        mock_auth_token,
        sample_patient,
    ):
        patient_data = {
            "phone": sample_patient.phone,  # Duplicate
            "email": "another@example.com",
            "first_name": "Another",
            "last_name": "Patient",
            "date_of_birth": "1990-01-01",
        }
        
        response = await client.post(
            "/api/v1/patients/",
            json=patient_data,
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    async def test_get_patient(self, client: AsyncClient, mock_auth_token, sample_patient):
        response = await client.get(
            f"/api/v1/patients/{sample_patient.id}",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sample_patient.id)
        assert data["phone"] == sample_patient.phone
        assert data["first_name"] == sample_patient.first_name
    
    async def test_get_patient_not_found(self, client: AsyncClient, mock_auth_token):
        import uuid
        fake_id = str(uuid.uuid4())
        
        response = await client.get(
            f"/api/v1/patients/{fake_id}",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 404
        assert "Patient not found" in response.json()["detail"]
    
    async def test_update_patient(self, client: AsyncClient, mock_auth_token, sample_patient):
        update_data = {
            "email": "updated@example.com",
            "language_preference": "hi",
        }
        
        response = await client.put(
            f"/api/v1/patients/{sample_patient.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == update_data["email"]
        assert data["language_preference"] == update_data["language_preference"]
        assert data["phone"] == sample_patient.phone  # Unchanged
    
    async def test_search_patients(self, client: AsyncClient, mock_auth_token, db_session):
        from app.models import Patient
        
        # Create multiple patients
        patients = [
            Patient(
                phone=f"987654320{i}",
                first_name=f"Test{i}",
                last_name="Patient",
                date_of_birth=date(1990, 1, 1),
            )
            for i in range(3)
        ]
        
        for patient in patients:
            db_session.add(patient)
        await db_session.commit()
        
        # Search without query
        response = await client.get(
            "/api/v1/patients/",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
    
    async def test_search_patients_with_query(
        self,
        client: AsyncClient,
        mock_auth_token,
        sample_patient,
    ):
        response = await client.get(
            f"/api/v1/patients/?q={sample_patient.first_name}",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(p["id"] == str(sample_patient.id) for p in data)
    
    async def test_search_patients_pagination(
        self,
        client: AsyncClient,
        mock_auth_token,
        db_session,
    ):
        from app.models import Patient
        
        # Create multiple patients
        for i in range(15):
            patient = Patient(
                phone=f"987654330{i:02d}",
                first_name=f"Batch{i}",
                last_name="Patient",
                date_of_birth=date(1990, 1, 1),
            )
            db_session.add(patient)
        await db_session.commit()
        
        # Get first page
        response = await client.get(
            "/api/v1/patients/?limit=5&offset=0",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        
        # Get second page
        response = await client.get(
            "/api/v1/patients/?limit=5&offset=5",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
    
    async def test_patient_api_requires_auth(self, client: AsyncClient):
        # Test without auth token
        response = await client.get("/api/v1/patients/")
        assert response.status_code == 401
        
        response = await client.post(
            "/api/v1/patients/",
            json={"phone": "9999999999"},
        )
        assert response.status_code == 401