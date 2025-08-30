"""
Load testing scenarios for Baymax backend using locust
Run with: locust -f tests/load/test_load.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
from datetime import datetime, timedelta
import random
import json


class BaymaxUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get auth token"""
        # Create a test provider account
        self.provider_email = f"loadtest_{random.randint(1000, 9999)}@example.com"
        self.client.post(
            "/api/v1/providers/",
            json={
                "email": self.provider_email,
                "phone": f"98765{random.randint(10000, 99999)}",
                "password": "Test@1234",
                "first_name": "Load",
                "last_name": "Test",
                "registration_number": f"MED{random.randint(10000, 99999)}",
                "specialization": "orthopedics",
            }
        )
        
        # Login
        response = self.client.post(
            "/api/v1/auth/login",
            data={
                "username": self.provider_email,
                "password": "Test@1234",
            }
        )
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}
    
    @task(3)
    def view_patients(self):
        """Search and view patient records"""
        self.client.get("/api/v1/patients/", headers=self.headers)
    
    @task(2)
    def create_patient(self):
        """Create a new patient"""
        self.client.post(
            "/api/v1/patients/",
            json={
                "phone": f"98764{random.randint(10000, 99999)}",
                "email": f"patient_{random.randint(1000, 9999)}@example.com",
                "first_name": "Test",
                "last_name": f"Patient{random.randint(1, 100)}",
                "date_of_birth": "1990-01-01",
                "gender": random.choice(["male", "female", "other"]),
            },
            headers=self.headers,
        )
    
    @task(4)
    def check_appointments(self):
        """View appointment list"""
        self.client.get("/api/v1/appointments/", headers=self.headers)
    
    @task(2)
    def check_available_slots(self):
        """Check available appointment slots"""
        tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
        provider_id = "00000000-0000-0000-0000-000000000000"  # Mock ID
        
        self.client.get(
            f"/api/v1/appointments/slots/available"
            f"?provider_id={provider_id}"
            f"&date={tomorrow}"
            f"&appointment_type=physical",
            headers=self.headers,
        )
    
    @task(1)
    def health_check(self):
        """Health check endpoint"""
        self.client.get("/health")


class IntakeWebSocketUser(HttpUser):
    """Simulates WebSocket intake sessions"""
    wait_time = between(2, 5)
    
    def on_start(self):
        """Initialize WebSocket session"""
        self.session_id = f"load_test_{random.randint(1000, 9999)}"
    
    @task
    def simulate_intake_session(self):
        """Simulate an intake conversation"""
        # Start session
        appointment_id = "00000000-0000-0000-0000-000000000000"
        response = self.client.post(
            f"/api/v1/intake/sessions/{appointment_id}/start"
        )
        
        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data["session_id"]
            
            # Check session status
            self.client.get(f"/api/v1/intake/sessions/{session_id}/status")
            
            # Note: WebSocket connections would be tested with a different tool
            # like websocket-bench or custom asyncio script


class PatientFlowUser(HttpUser):
    """Simulates complete patient flow"""
    wait_time = between(2, 4)
    
    def on_start(self):
        """Setup patient authentication"""
        self.phone = f"98763{random.randint(10000, 99999)}"
    
    @task
    def complete_patient_flow(self):
        """Simulate complete patient journey"""
        # 1. Request OTP
        with self.client.post(
            "/api/v1/auth/otp/request",
            json={"phone": self.phone},
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure("OTP request failed")
        
        # 2. Verify OTP (mocked)
        with self.client.post(
            "/api/v1/auth/otp/verify",
            json={"phone": self.phone, "otp": "123456"},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
            else:
                response.failure("OTP verification failed")
                return
        
        # 3. Search for providers
        self.client.get(
            "/api/v1/providers/?specialization=orthopedics",
            headers=self.headers,
        )
        
        # 4. Check available slots
        tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
        self.client.get(
            f"/api/v1/appointments/slots/available"
            f"?provider_id=00000000-0000-0000-0000-000000000000"
            f"&date={tomorrow}",
            headers=self.headers,
        )


class HighLoadScenario(HttpUser):
    """Stress test with high concurrency"""
    wait_time = between(0.1, 0.5)  # Aggressive timing
    
    @task(10)
    def rapid_reads(self):
        """High frequency read operations"""
        endpoints = [
            "/health",
            "/health/ready",
            "/api/v1/patients/",
            "/api/v1/appointments/",
            "/api/v1/providers/",
        ]
        
        endpoint = random.choice(endpoints)
        self.client.get(endpoint, headers=getattr(self, 'headers', {}))
    
    @task(2)
    def rapid_writes(self):
        """Lower frequency write operations"""
        # Create appointment
        self.client.post(
            "/api/v1/appointments/",
            json={
                "patient_id": "00000000-0000-0000-0000-000000000000",
                "provider_id": "00000000-0000-0000-0000-000000000000",
                "appointment_type": "physical",
                "scheduled_at": (datetime.utcnow() + timedelta(days=random.randint(1, 30))).isoformat(),
                "duration_minutes": 30,
            },
            headers=getattr(self, 'headers', {}),
        )