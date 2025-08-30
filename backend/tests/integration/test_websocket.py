import pytest
import json
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.asyncio
class TestWebSocketIntake:
    def test_websocket_connection(self):
        """Test WebSocket connection establishment"""
        client = TestClient(app)
        
        with patch("app.api.intake.AIIntakeService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_text_input = AsyncMock(
                return_value={
                    "type": "ai_response",
                    "content": "Hello, how can I help you?",
                    "language": "en",
                    "confidence": 0.95,
                }
            )
            
            with client.websocket_connect("/api/v1/intake/ws/test_session") as websocket:
                # Send a message
                websocket.send_json({
                    "type": "text_message",
                    "content": "Hello",
                    "language": "en",
                })
                
                # Receive response
                data = websocket.receive_json()
                assert data["type"] == "ai_response"
                assert "content" in data
    
    def test_websocket_text_conversation(self):
        """Test text-based conversation over WebSocket"""
        client = TestClient(app)
        
        with patch("app.api.intake.AIIntakeService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_text_input = AsyncMock(
                return_value={
                    "type": "ai_response",
                    "content": "Can you describe your pain?",
                    "language": "en",
                    "confidence": 0.95,
                }
            )
            
            with client.websocket_connect("/api/v1/intake/ws/test_session") as websocket:
                # Patient describes symptoms
                websocket.send_json({
                    "type": "text_message",
                    "content": "I have knee pain when walking",
                    "language": "en",
                })
                
                response = websocket.receive_json()
                assert response["type"] == "ai_response"
                assert "pain" in response["content"].lower()
    
    def test_websocket_red_flag_alert(self):
        """Test red flag detection and alert over WebSocket"""
        client = TestClient(app)
        
        with patch("app.api.intake.AIIntakeService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_text_input = AsyncMock(
                return_value={
                    "type": "red_flag_alert",
                    "message": "Please seek immediate medical attention",
                    "severity": "critical",
                    "escalation_triggered": True,
                }
            )
            mock_instance.escalate_red_flag = AsyncMock()
            
            with client.websocket_connect("/api/v1/intake/ws/emergency_session") as websocket:
                # Send emergency symptom
                websocket.send_json({
                    "type": "text_message",
                    "content": "I can't feel my legs",
                    "language": "en",
                })
                
                response = websocket.receive_json()
                assert response["type"] == "red_flag_alert"
                assert response["escalation_triggered"] is True
                assert response["severity"] == "critical"
    
    def test_websocket_session_completion(self):
        """Test session completion over WebSocket"""
        client = TestClient(app)
        
        with patch("app.api.intake.AIIntakeService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.complete_session = AsyncMock(
                return_value={
                    "session_id": "test_session",
                    "completed": True,
                    "completion_score": 0.85,
                    "total_turns": 10,
                    "chief_complaint": "Knee pain",
                    "hpi_collected": True,
                    "pmh_collected": True,
                    "medications_collected": True,
                    "allergies_collected": True,
                    "ros_collected": False,
                    "red_flags_detected": [],
                    "summary": {"status": "completed"},
                }
            )
            
            with client.websocket_connect("/api/v1/intake/ws/test_session") as websocket:
                # Send session end signal
                websocket.send_json({
                    "type": "end_session",
                })
                
                response = websocket.receive_json()
                assert response["type"] == "session_complete"
                assert response["data"]["completed"] is True
                assert response["data"]["completion_score"] == 0.85
    
    def test_websocket_error_handling(self):
        """Test error handling in WebSocket connection"""
        client = TestClient(app)
        
        with patch("app.api.intake.AIIntakeService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_text_input = AsyncMock(
                side_effect=Exception("Processing error")
            )
            
            with client.websocket_connect("/api/v1/intake/ws/error_session") as websocket:
                # Send message that causes error
                websocket.send_json({
                    "type": "text_message",
                    "content": "Test message",
                    "language": "en",
                })
                
                response = websocket.receive_json()
                assert response["type"] == "error"
                assert "error occurred" in response["message"].lower()
    
    def test_websocket_invalid_message_type(self):
        """Test handling of invalid message types"""
        client = TestClient(app)
        
        with client.websocket_connect("/api/v1/intake/ws/test_session") as websocket:
            # Send invalid message type
            websocket.send_json({
                "type": "invalid_type",
                "data": "test",
            })
            
            # Connection should handle gracefully
            # In production, this might send an error response
            # or ignore the message


@pytest.mark.asyncio
class TestIntakeSessionManagement:
    async def test_start_intake_session(self, client, mock_auth_token, sample_appointment):
        """Test starting a new intake session"""
        response = await client.post(
            f"/api/v1/intake/sessions/{sample_appointment.id}/start",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "websocket_url" in data
        assert data["status"] == "ready"
        assert f"/api/v1/intake/ws/" in data["websocket_url"]
    
    async def test_get_session_status(self, client, mock_auth_token):
        """Test getting session status"""
        # First create a session
        import uuid
        appointment_id = str(uuid.uuid4())
        
        create_response = await client.post(
            f"/api/v1/intake/sessions/{appointment_id}/start",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        session_id = create_response.json()["session_id"]
        
        # Get status
        with patch("app.api.intake.AIIntakeService") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.get_session_status = AsyncMock(
                return_value={
                    "session_id": session_id,
                    "status": "active",
                    "started_at": "2024-01-01T10:00:00",
                    "last_activity_at": "2024-01-01T10:05:00",
                    "total_turns": 5,
                    "red_flags_count": 0,
                }
            )
            
            response = await client.get(
                f"/api/v1/intake/sessions/{session_id}/status",
                headers={"Authorization": f"Bearer {mock_auth_token}"},
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert data["status"] == "active"
        assert data["total_turns"] == 5
    
    async def test_get_nonexistent_session_status(self, client, mock_auth_token):
        """Test getting status of non-existent session"""
        response = await client.get(
            "/api/v1/intake/sessions/nonexistent_session/status",
            headers={"Authorization": f"Bearer {mock_auth_token}"},
        )
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]