"""Value objects for Patient domain."""
import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

from app.domain.shared.value_object import ValueObject


@dataclass(frozen=True)
class PhoneNumber(ValueObject):
    """Phone number value object with validation."""
    
    number: str
    country_code: str = "+91"
    
    def validate(self) -> None:
        """Validate Indian phone number format."""
        # Remove spaces and hyphens
        clean_number = re.sub(r'[\s-]', '', self.number)
        
        # Indian phone number validation
        if not re.match(r'^[6-9]\d{9}$', clean_number):
            raise ValueError(f"Invalid Indian phone number: {self.number}")
    
    @property
    def formatted(self) -> str:
        """Return formatted phone number."""
        clean = re.sub(r'[\s-]', '', self.number)
        return f"{self.country_code} {clean[:5]} {clean[5:]}"
    
    @property
    def masked(self) -> str:
        """Return masked phone number for display."""
        clean = re.sub(r'[\s-]', '', self.number)
        return f"{self.country_code} XXXXX {clean[-4:]}"


@dataclass(frozen=True)
class EmailAddress(ValueObject):
    """Email address value object."""
    
    value: str
    
    def validate(self) -> None:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, self.value):
            raise ValueError(f"Invalid email address: {self.value}")
    
    @property
    def domain(self) -> str:
        """Extract domain from email."""
        return self.value.split('@')[1]
    
    @property
    def masked(self) -> str:
        """Return masked email for display."""
        local, domain = self.value.split('@')
        if len(local) <= 3:
            masked_local = '*' * len(local)
        else:
            masked_local = local[:2] + '*' * (len(local) - 3) + local[-1]
        return f"{masked_local}@{domain}"


@dataclass(frozen=True)
class ABHANumber(ValueObject):
    """ABHA (Ayushman Bharat Health Account) number value object."""
    
    value: str
    
    def validate(self) -> None:
        """Validate ABHA number format (14 digits or 17 with hyphens)."""
        clean = re.sub(r'-', '', self.value)
        if not re.match(r'^\d{14}$', clean):
            raise ValueError(f"Invalid ABHA number: {self.value}")
    
    @property
    def formatted(self) -> str:
        """Return formatted ABHA number (XX-XXXX-XXXX-XXXX)."""
        clean = re.sub(r'-', '', self.value)
        return f"{clean[:2]}-{clean[2:6]}-{clean[6:10]}-{clean[10:]}"
    
    @property
    def masked(self) -> str:
        """Return masked ABHA for display."""
        clean = re.sub(r'-', '', self.value)
        return f"XX-XXXX-XXXX-{clean[-4:]}"


@dataclass(frozen=True)
class PatientName(ValueObject):
    """Patient name value object."""
    
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    
    def validate(self) -> None:
        """Validate name fields."""
        if not self.first_name or not self.first_name.strip():
            raise ValueError("First name is required")
        if not self.last_name or not self.last_name.strip():
            raise ValueError("Last name is required")
        
        # Check for valid characters (letters, spaces, apostrophes, hyphens)
        name_pattern = r"^[a-zA-Z\s'-]+$"
        if not re.match(name_pattern, self.first_name):
            raise ValueError(f"Invalid first name: {self.first_name}")
        if not re.match(name_pattern, self.last_name):
            raise ValueError(f"Invalid last name: {self.last_name}")
        if self.middle_name and not re.match(name_pattern, self.middle_name):
            raise ValueError(f"Invalid middle name: {self.middle_name}")
    
    @property
    def full_name(self) -> str:
        """Return full name."""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)
    
    @property
    def initials(self) -> str:
        """Return initials."""
        initials = self.first_name[0].upper()
        if self.middle_name:
            initials += self.middle_name[0].upper()
        initials += self.last_name[0].upper()
        return initials


@dataclass(frozen=True)
class DateOfBirth(ValueObject):
    """Date of birth value object with age calculation."""
    
    value: date
    
    def validate(self) -> None:
        """Validate date of birth."""
        if self.value > date.today():
            raise ValueError("Date of birth cannot be in the future")
        
        # Check for reasonable age (0-150 years)
        age = self.calculate_age()
        if age < 0 or age > 150:
            raise ValueError(f"Invalid age: {age}")
    
    def calculate_age(self) -> int:
        """Calculate current age."""
        today = date.today()
        age = today.year - self.value.year
        if (today.month, today.day) < (self.value.month, self.value.day):
            age -= 1
        return age
    
    @property
    def age(self) -> int:
        """Current age."""
        return self.calculate_age()
    
    @property
    def is_minor(self) -> bool:
        """Check if patient is a minor (under 18)."""
        return self.age < 18
    
    @property
    def is_senior(self) -> bool:
        """Check if patient is a senior citizen (60+ in India)."""
        return self.age >= 60


@dataclass(frozen=True)
class Gender(ValueObject):
    """Gender value object."""
    
    value: str
    
    VALID_GENDERS = {"male", "female", "other", "prefer_not_to_say"}
    
    def validate(self) -> None:
        """Validate gender value."""
        if self.value.lower() not in self.VALID_GENDERS:
            raise ValueError(f"Invalid gender: {self.value}. Must be one of {self.VALID_GENDERS}")
    
    @property
    def normalized(self) -> str:
        """Return normalized gender value."""
        return self.value.lower()
    
    @property
    def pronoun(self) -> str:
        """Return appropriate pronoun."""
        pronouns = {
            "male": "he/him",
            "female": "she/her",
            "other": "they/them",
            "prefer_not_to_say": "they/them"
        }
        return pronouns.get(self.normalized, "they/them")


@dataclass(frozen=True)
class Address(ValueObject):
    """Address value object for Indian addresses."""
    
    line1: str
    line2: Optional[str]
    city: str
    state: str
    pincode: str
    country: str = "India"
    
    INDIAN_STATES = {
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
        "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
        "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
    }
    
    def validate(self) -> None:
        """Validate Indian address."""
        if not self.line1 or not self.line1.strip():
            raise ValueError("Address line 1 is required")
        if not self.city or not self.city.strip():
            raise ValueError("City is required")
        if self.state not in self.INDIAN_STATES:
            raise ValueError(f"Invalid Indian state: {self.state}")
        
        # Validate Indian pincode (6 digits)
        if not re.match(r'^\d{6}$', self.pincode):
            raise ValueError(f"Invalid Indian pincode: {self.pincode}")
    
    @property
    def formatted(self) -> str:
        """Return formatted address."""
        lines = [self.line1]
        if self.line2:
            lines.append(self.line2)
        lines.append(f"{self.city}, {self.state} {self.pincode}")
        lines.append(self.country)
        return "\n".join(lines)
    
    @property
    def single_line(self) -> str:
        """Return single-line address."""
        parts = [self.line1]
        if self.line2:
            parts.append(self.line2)
        parts.extend([self.city, self.state, self.pincode, self.country])
        return ", ".join(parts)