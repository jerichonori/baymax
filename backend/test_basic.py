#!/usr/bin/env python
"""Basic test to verify core functionality without database dependencies"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that core modules can be imported"""
    print("Testing imports...")
    
    try:
        from app.core.security import create_access_token, verify_password, get_password_hash
        print("✓ Security module imported")
    except Exception as e:
        print(f"✗ Security module failed: {e}")
        return False
    
    try:
        from app.schemas.patient import PatientCreate
        from app.schemas.auth import OTPRequest
        print("✓ Schemas imported")
    except Exception as e:
        print(f"✗ Schemas failed: {e}")
        return False
    
    return True

def test_security_functions():
    """Test security functions work"""
    print("\nTesting security functions...")
    
    from app.core.security import create_access_token, verify_token, get_password_hash, verify_password
    
    # Test JWT tokens
    token = create_access_token(subject="test_user")
    user_id = verify_token(token)
    assert user_id == "test_user", "Token verification failed"
    print("✓ JWT token creation and verification")
    
    # Test password hashing
    password = "Test@1234"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed), "Password verification failed"
    print("✓ Password hashing and verification")
    
    return True

def test_schema_validation():
    """Test Pydantic schemas"""
    print("\nTesting schema validation...")
    
    from datetime import date
    from app.schemas.patient import PatientCreate
    from app.schemas.auth import OTPRequest
    
    # Test valid patient
    patient = PatientCreate(
        phone="9876543210",
        email="test@example.com",
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1990, 1, 1),
        gender="male"
    )
    assert patient.phone == "9876543210"
    print("✓ Patient schema validation")
    
    # Test OTP request
    otp_req = OTPRequest(phone="9876543210")
    assert otp_req.phone == "9876543210"
    print("✓ OTP schema validation")
    
    # Test invalid phone (should raise error)
    try:
        from pydantic import ValidationError
        OTPRequest(phone="123")
        print("✗ Should have failed validation for short phone")
        return False
    except ValidationError:
        print("✓ Invalid data correctly rejected")
    
    return True

def test_api_creation():
    """Test that FastAPI app can be created"""
    print("\nTesting FastAPI app creation...")
    
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        app = FastAPI()
        
        @app.get("/test")
        def test_endpoint():
            return {"status": "ok"}
        
        client = TestClient(app)
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        print("✓ FastAPI app creation and basic endpoint")
        
    except Exception as e:
        print(f"✗ FastAPI test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("BAYMAX BACKEND - BASIC FUNCTIONALITY TEST")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_security_functions,
        test_schema_validation,
        test_api_creation,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)