#!/usr/bin/env python
"""Test suite for Domain layer with DDD patterns."""

import sys
import os
from datetime import date, datetime, timedelta
from uuid import uuid4

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set required environment variables
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test:test@localhost:5432/test"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing"


def test_value_objects():
    """Test domain value objects."""
    print("\n📦 DOMAIN VALUE OBJECTS")
    print("-" * 40)
    
    from app.domain.patient.value_objects import (
        PhoneNumber, EmailAddress, ABHANumber,
        PatientName, DateOfBirth, Gender, Address
    )
    
    tests_passed = []
    
    # Test PhoneNumber
    try:
        phone = PhoneNumber(number="9876543210")
        assert phone.formatted == "+91 98765 43210"
        assert phone.masked == "+91 XXXXX 3210"
        tests_passed.append(True)
        print("  ✓ PhoneNumber validation and formatting")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ PhoneNumber failed: {e}")
    
    # Test invalid phone
    try:
        PhoneNumber(number="123")  # Too short
        tests_passed.append(False)
        print("  ✗ Invalid phone accepted")
    except ValueError:
        tests_passed.append(True)
        print("  ✓ Invalid phone rejected")
    
    # Test EmailAddress
    try:
        email = EmailAddress(value="test@example.com")
        assert email.domain == "example.com"
        assert email.masked == "te*t@example.com"
        tests_passed.append(True)
        print("  ✓ EmailAddress validation")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ EmailAddress failed: {e}")
    
    # Test ABHANumber
    try:
        abha = ABHANumber(value="12345678901234")
        assert abha.formatted == "12-3456-7890-1234"
        assert abha.masked == "XX-XXXX-XXXX-1234"
        tests_passed.append(True)
        print("  ✓ ABHANumber validation")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ ABHANumber failed: {e}")
    
    # Test PatientName
    try:
        name = PatientName(first_name="John", last_name="Doe", middle_name="Smith")
        assert name.full_name == "John Smith Doe"
        assert name.initials == "JSD"
        tests_passed.append(True)
        print("  ✓ PatientName validation")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ PatientName failed: {e}")
    
    # Test DateOfBirth
    try:
        dob = DateOfBirth(value=date(1990, 1, 1))
        assert dob.age > 30
        assert not dob.is_minor
        assert not dob.is_senior
        tests_passed.append(True)
        print("  ✓ DateOfBirth with age calculation")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ DateOfBirth failed: {e}")
    
    # Test Gender
    try:
        gender = Gender(value="male")
        assert gender.normalized == "male"
        assert gender.pronoun == "he/him"
        tests_passed.append(True)
        print("  ✓ Gender validation")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Gender failed: {e}")
    
    # Test Address
    try:
        address = Address(
            line1="123 Main St",
            line2="Apt 4B",
            city="Mumbai",
            state="Maharashtra",
            pincode="400001"
        )
        assert "Mumbai" in address.formatted
        tests_passed.append(True)
        print("  ✓ Address validation")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Address failed: {e}")
    
    print(f"\n  Result: {sum(tests_passed)}/{len(tests_passed)} value objects validated")
    return all(tests_passed)


def test_patient_aggregate():
    """Test Patient aggregate root."""
    print("\n👤 PATIENT AGGREGATE ROOT")
    print("-" * 40)
    
    from app.domain.patient.aggregate import Patient
    from app.domain.patient.value_objects import (
        PhoneNumber, EmailAddress, PatientName,
        DateOfBirth, Gender
    )
    
    tests_passed = []
    
    # Test patient registration
    try:
        patient = Patient.register(
            id=uuid4(),
            phone=PhoneNumber(number="9876543210"),
            name=PatientName(first_name="Test", last_name="Patient"),
            date_of_birth=DateOfBirth(value=date(1990, 1, 1)),
            gender=Gender(value="male"),
            email=EmailAddress(value="test@example.com")
        )
        
        assert not patient.is_verified
        assert patient.is_active
        assert len(patient._events) > 0  # Should have registration event
        tests_passed.append(True)
        print("  ✓ Patient registration with domain event")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Patient registration failed: {e}")
    
    # Test patient verification
    try:
        patient.verify()
        assert patient.is_verified
        assert patient.verified_at is not None
        tests_passed.append(True)
        print("  ✓ Patient verification")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Patient verification failed: {e}")
    
    # Test consent management
    try:
        consent = patient.grant_consent(
            consent_id=uuid4(),
            consent_type="ai_intake",
            purpose="AI-assisted medical intake"
        )
        assert consent.is_active
        assert patient.has_active_consent("ai_intake")
        tests_passed.append(True)
        print("  ✓ Consent management")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Consent management failed: {e}")
    
    # Test consent revocation
    try:
        patient.revoke_consent("ai_intake")
        assert not patient.has_active_consent("ai_intake")
        tests_passed.append(True)
        print("  ✓ Consent revocation")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Consent revocation failed: {e}")
    
    # Test emergency contact
    try:
        contact = patient.add_emergency_contact(
            contact_id=uuid4(),
            name=PatientName(first_name="Emergency", last_name="Contact"),
            phone=PhoneNumber(number="9876543211"),
            relationship="Spouse",
            is_primary=True
        )
        assert contact.is_primary
        assert len(patient.emergency_contacts) == 1
        tests_passed.append(True)
        print("  ✓ Emergency contact management")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Emergency contact failed: {e}")
    
    # Test invariant validation
    try:
        # Test minor without emergency contact (should fail invariant)
        minor_patient = Patient.register(
            id=uuid4(),
            phone=PhoneNumber(number="9876543212"),
            name=PatientName(first_name="Minor", last_name="Patient"),
            date_of_birth=DateOfBirth(value=date(2010, 1, 1)),  # Minor
            gender=Gender(value="male")
        )
        
        # This should raise error when validating invariants
        try:
            minor_patient.validate_invariants()
            tests_passed.append(False)
            print("  ✗ Minor invariant not enforced")
        except ValueError:
            tests_passed.append(True)
            print("  ✓ Minor invariant enforced")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Invariant validation failed: {e}")
    
    print(f"\n  Result: {sum(tests_passed)}/{len(tests_passed)} aggregate tests passed")
    return all(tests_passed)


def test_domain_services():
    """Test domain services."""
    print("\n⚙️ DOMAIN SERVICES")
    print("-" * 40)
    
    from app.domain.patient.services import (
        PatientDuplicationChecker,
        PatientRegistrationService,
        PatientConsentService,
        PatientEligibilityService
    )
    from app.domain.patient.repository import PatientRepository
    from app.domain.patient.aggregate import Patient
    from app.domain.patient.value_objects import (
        PhoneNumber, PatientName, DateOfBirth, Gender
    )
    
    # Create mock repository
    class MockPatientRepository(PatientRepository):
        def __init__(self):
            self.patients = {}
        
        async def find_by_id(self, patient_id):
            return self.patients.get(patient_id)
        
        async def find_by_phone(self, phone):
            for patient in self.patients.values():
                if patient.phone == phone:
                    return patient
            return None
        
        async def find_by_abha(self, abha):
            for patient in self.patients.values():
                if patient.abha_number == abha:
                    return patient
            return None
        
        async def find_by_specification(self, spec):
            return [p for p in self.patients.values() if spec.is_satisfied_by(p)]
        
        async def save(self, patient):
            self.patients[patient.id] = patient
        
        async def update(self, patient):
            self.patients[patient.id] = patient
        
        async def delete(self, patient_id):
            if patient_id in self.patients:
                del self.patients[patient_id]
        
        async def exists_by_phone(self, phone):
            return await self.find_by_phone(phone) is not None
        
        async def exists_by_abha(self, abha):
            return await self.find_by_abha(abha) is not None
        
        async def count(self):
            return len(self.patients)
        
        async def count_active(self):
            return sum(1 for p in self.patients.values() if p.is_active)
    
    tests_passed = []
    
    # Test duplication checker
    try:
        import asyncio
        repo = MockPatientRepository()
        dup_checker = PatientDuplicationChecker(repo)
        
        # Should not find duplicate initially
        phone = PhoneNumber(number="9876543213")
        result = asyncio.run(dup_checker.is_duplicate_phone(phone))
        assert not result
        tests_passed.append(True)
        print("  ✓ Duplication checker - no duplicates")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Duplication checker failed: {e}")
    
    # Test registration service
    try:
        reg_service = PatientRegistrationService(repo, dup_checker)
        
        patient = asyncio.run(reg_service.register_patient(
            phone=PhoneNumber(number="9876543214"),
            name=PatientName(first_name="Service", last_name="Test"),
            date_of_birth=DateOfBirth(value=date(1990, 1, 1)),
            gender=Gender(value="female")
        ))
        
        assert patient.id in repo.patients
        tests_passed.append(True)
        print("  ✓ Registration service")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Registration service failed: {e}")
    
    # Test consent service
    try:
        consent_service = PatientConsentService(repo)
        
        # Grant intake consent
        asyncio.run(consent_service.grant_intake_consent(patient.id))
        
        # Check consent
        has_consent = asyncio.run(consent_service.check_intake_consent(patient.id))
        assert has_consent
        tests_passed.append(True)
        print("  ✓ Consent service")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Consent service failed: {e}")
    
    # Test eligibility service
    try:
        eligibility_service = PatientEligibilityService(repo)
        
        # Patient needs verification for telehealth
        patient.verify()
        patient.grant_consent(uuid4(), "telehealth", "Telehealth services")
        asyncio.run(repo.update(patient))
        
        eligible = asyncio.run(eligibility_service.is_eligible_for_telehealth(patient.id))
        assert eligible
        tests_passed.append(True)
        print("  ✓ Eligibility service")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Eligibility service failed: {e}")
    
    print(f"\n  Result: {sum(tests_passed)}/{len(tests_passed)} service tests passed")
    return all(tests_passed)


def test_specifications():
    """Test specification pattern."""
    print("\n🔍 SPECIFICATION PATTERN")
    print("-" * 40)
    
    from app.domain.patient.specifications import (
        ActivePatientsSpecification,
        VerifiedPatientsSpecification,
        MinorPatientsSpecification,
        PatientsWithConsentSpecification
    )
    from app.domain.patient.aggregate import Patient
    from app.domain.patient.value_objects import (
        PhoneNumber, PatientName, DateOfBirth, Gender
    )
    
    tests_passed = []
    
    # Create test patients
    adult_patient = Patient.register(
        id=uuid4(),
        phone=PhoneNumber(number="9876543215"),
        name=PatientName(first_name="Adult", last_name="Patient"),
        date_of_birth=DateOfBirth(value=date(1990, 1, 1)),
        gender=Gender(value="male")
    )
    adult_patient.verify()
    
    minor_patient = Patient.register(
        id=uuid4(),
        phone=PhoneNumber(number="9876543216"),
        name=PatientName(first_name="Minor", last_name="Patient"),
        date_of_birth=DateOfBirth(value=date(2010, 1, 1)),
        gender=Gender(value="female")
    )
    
    # Test specifications
    try:
        active_spec = ActivePatientsSpecification()
        assert active_spec.is_satisfied_by(adult_patient)
        assert active_spec.is_satisfied_by(minor_patient)
        tests_passed.append(True)
        print("  ✓ Active patients specification")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Active specification failed: {e}")
    
    try:
        verified_spec = VerifiedPatientsSpecification()
        assert verified_spec.is_satisfied_by(adult_patient)
        assert not verified_spec.is_satisfied_by(minor_patient)
        tests_passed.append(True)
        print("  ✓ Verified patients specification")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Verified specification failed: {e}")
    
    try:
        minor_spec = MinorPatientsSpecification()
        assert not minor_spec.is_satisfied_by(adult_patient)
        assert minor_spec.is_satisfied_by(minor_patient)
        tests_passed.append(True)
        print("  ✓ Minor patients specification")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Minor specification failed: {e}")
    
    # Test composite specifications
    try:
        # Verified AND Active
        composite_spec = verified_spec.and_(active_spec)
        assert composite_spec.is_satisfied_by(adult_patient)
        assert not composite_spec.is_satisfied_by(minor_patient)
        
        # Minor OR Verified
        or_spec = minor_spec.or_(verified_spec)
        assert or_spec.is_satisfied_by(adult_patient)
        assert or_spec.is_satisfied_by(minor_patient)
        
        tests_passed.append(True)
        print("  ✓ Composite specifications (AND/OR)")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Composite specification failed: {e}")
    
    print(f"\n  Result: {sum(tests_passed)}/{len(tests_passed)} specification tests passed")
    return all(tests_passed)


def test_intake_value_objects():
    """Test intake domain value objects."""
    print("\n🎤 INTAKE VALUE OBJECTS")
    print("-" * 40)
    
    from app.domain.intake.value_objects import (
        Language, ChiefComplaint, Symptom, VitalSigns,
        RedFlag, RedFlagSeverity, OrthopedicAssessment,
        IntakeCompleteness
    )
    
    tests_passed = []
    
    # Test Language
    try:
        lang = Language(code="hi", name="Hindi", confidence=0.95)
        assert lang.code == "hi"
        tests_passed.append(True)
        print("  ✓ Language value object")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Language failed: {e}")
    
    # Test ChiefComplaint
    try:
        complaint = ChiefComplaint(
            description="Severe knee pain",
            duration="3 days",
            severity=8
        )
        assert complaint.severity == 8
        tests_passed.append(True)
        print("  ✓ Chief complaint validation")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Chief complaint failed: {e}")
    
    # Test VitalSigns with BMI calculation
    try:
        vitals = VitalSigns(
            temperature=37.2,
            blood_pressure_systolic=120,
            blood_pressure_diastolic=80,
            heart_rate=72,
            weight=70,
            height=175
        )
        assert vitals.bmi == 22.9
        tests_passed.append(True)
        print("  ✓ Vital signs with BMI calculation")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Vital signs failed: {e}")
    
    # Test RedFlag
    try:
        red_flag = RedFlag(
            condition="Cauda equina syndrome",
            severity=RedFlagSeverity.CRITICAL,
            detected_at=datetime.utcnow(),
            context="Patient reports loss of bladder control",
            confidence=0.95
        )
        assert red_flag.escalation_required  # Critical always requires escalation
        tests_passed.append(True)
        print("  ✓ Red flag with auto-escalation")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Red flag failed: {e}")
    
    # Test OrthopedicAssessment
    try:
        ortho = OrthopedicAssessment(
            mechanism_of_injury="Fall from height",
            weight_bearing_status=False,
            deformity_noted=True
        )
        assert ortho.is_high_risk()
        tests_passed.append(True)
        print("  ✓ Orthopedic assessment with risk detection")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Orthopedic assessment failed: {e}")
    
    # Test IntakeCompleteness
    try:
        completeness = IntakeCompleteness(
            chief_complaint_collected=True,
            hpi_collected=True,
            medications_collected=True,
            allergies_collected=True
        )
        assert completeness.is_complete
        assert completeness.score == 0.5  # 4 out of 8 sections
        assert "Past Medical History" in completeness.missing_sections
        tests_passed.append(True)
        print("  ✓ Intake completeness tracking")
    except Exception as e:
        tests_passed.append(False)
        print(f"  ✗ Intake completeness failed: {e}")
    
    print(f"\n  Result: {sum(tests_passed)}/{len(tests_passed)} intake value objects validated")
    return all(tests_passed)


def main():
    """Run all domain tests."""
    print("=" * 50)
    print("DOMAIN LAYER - DDD ARCHITECTURE TESTS")
    print("=" * 50)
    
    test_results = {}
    
    # Run test suites
    test_suites = [
        ("Value Objects", test_value_objects),
        ("Patient Aggregate", test_patient_aggregate),
        ("Domain Services", test_domain_services),
        ("Specifications", test_specifications),
        ("Intake Value Objects", test_intake_value_objects),
    ]
    
    for suite_name, test_func in test_suites:
        try:
            test_results[suite_name] = test_func()
        except Exception as e:
            print(f"\n❌ {suite_name} suite failed: {e}")
            test_results[suite_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    for suite, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {suite}: {status}")
    
    total_passed = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"\nOverall: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL DOMAIN TESTS PASSED! DDD architecture is functional.")
    else:
        print("\n⚠️  Some domain tests failed. Review the output above.")
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)