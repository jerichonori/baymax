import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_password,
    get_password_hash,
    generate_otp,
    hash_otp,
    verify_otp,
    phi_encryption,
)
from app.core.config import settings


class TestJWTTokens:
    def test_create_access_token(self):
        subject = "test_user_id"
        token = create_access_token(subject=subject, scopes=["provider"])
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == subject
        assert payload["type"] == "access"
        assert "provider" in payload["scopes"]
    
    def test_create_refresh_token(self):
        subject = "test_user_id"
        token = create_refresh_token(subject=subject)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == subject
        assert payload["type"] == "refresh"
    
    def test_verify_valid_access_token(self):
        subject = "test_user_id"
        token = create_access_token(subject=subject)
        
        verified_subject = verify_token(token, token_type="access")
        assert verified_subject == subject
    
    def test_verify_invalid_token(self):
        verified_subject = verify_token("invalid_token", token_type="access")
        assert verified_subject is None
    
    def test_verify_expired_token(self):
        subject = "test_user_id"
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(subject=subject, expires_delta=expires_delta)
        
        verified_subject = verify_token(token, token_type="access")
        assert verified_subject is None
    
    def test_verify_wrong_token_type(self):
        subject = "test_user_id"
        access_token = create_access_token(subject=subject)
        
        # Try to verify access token as refresh token
        verified_subject = verify_token(access_token, token_type="refresh")
        assert verified_subject is None


class TestPasswordHashing:
    def test_password_hash_and_verify(self):
        password = "Test@1234"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
    
    def test_verify_wrong_password(self):
        password = "Test@1234"
        wrong_password = "Wrong@1234"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_same_password_different_hashes(self):
        password = "Test@1234"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2  # Bcrypt uses salt
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestOTP:
    def test_generate_otp(self):
        otp = generate_otp()
        
        assert len(otp) == settings.OTP_LENGTH
        assert otp.isdigit()
    
    def test_otp_hash_and_verify(self):
        otp = "123456"
        phone = "9876543210"
        hashed = hash_otp(otp, phone)
        
        assert verify_otp(otp, phone, hashed) is True
    
    def test_verify_wrong_otp(self):
        otp = "123456"
        wrong_otp = "654321"
        phone = "9876543210"
        hashed = hash_otp(otp, phone)
        
        assert verify_otp(wrong_otp, phone, hashed) is False
    
    def test_otp_hash_phone_specific(self):
        otp = "123456"
        phone1 = "9876543210"
        phone2 = "9876543211"
        
        hash1 = hash_otp(otp, phone1)
        hash2 = hash_otp(otp, phone2)
        
        assert hash1 != hash2
        assert verify_otp(otp, phone1, hash1) is True
        assert verify_otp(otp, phone2, hash1) is False


class TestPHIEncryption:
    def test_encrypt_decrypt(self):
        original_data = "Sensitive patient information"
        
        encrypted = phi_encryption.encrypt(original_data)
        decrypted = phi_encryption.decrypt(encrypted)
        
        assert encrypted != original_data
        assert decrypted == original_data
    
    def test_encrypted_data_different(self):
        data = "Patient data"
        
        encrypted1 = phi_encryption.encrypt(data)
        encrypted2 = phi_encryption.encrypt(data)
        
        # Fernet includes timestamp, so same data encrypts differently
        assert encrypted1 != encrypted2
        
        # But both decrypt to same value
        assert phi_encryption.decrypt(encrypted1) == data
        assert phi_encryption.decrypt(encrypted2) == data
    
    def test_decrypt_invalid_data(self):
        with pytest.raises(Exception):
            phi_encryption.decrypt("invalid_encrypted_data")