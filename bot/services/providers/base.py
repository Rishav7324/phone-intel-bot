"""Base models and abstract provider interface for phone intelligence lookups."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class NumberStatus(str, Enum):
    """Validation status classification for a phone number."""
    VALID = "VALID"
    POSSIBLE = "POSSIBLE"
    INVALID = "INVALID"


class PhoneMetadata(BaseModel):
    """Normalized, structured phone intelligence metadata."""

    input_number: str
    status: NumberStatus
    is_valid: bool = False
    is_possible: bool = False

    # Calling Code and ISO Region
    country_code: Optional[int] = None
    country_calling_code_str: Optional[str] = None
    region_code: Optional[str] = None
    country_name: str = "Not available"

    # Type & Carrier
    number_type: str = "Unknown"
    carrier: str = "Not available"
    region_description: str = "Not available"
    timezones: List[str] = Field(default_factory=lambda: ["Not available"])

    # Formats
    e164_format: Optional[str] = None
    international_format: Optional[str] = None
    national_format: Optional[str] = None
    rfc3966_format: Optional[str] = None

    # Flags & Diagnostics
    used_default_region: bool = False
    error_message: Optional[str] = None


class PhoneLookupProvider(ABC):
    """Abstract base class for all phone lookup providers."""

    @abstractmethod
    async def lookup(
        self,
        phone_number: str,
        default_region: Optional[str] = None
    ) -> PhoneMetadata:
        """Parse, validate, and retrieve metadata for a given phone number.

        Args:
            phone_number: Raw sanitized phone number string.
            default_region: Optional fallback ISO 3166-1 alpha-2 region code (e.g., 'IN', 'US').

        Returns:
            Structured PhoneMetadata instance.
        """
        raise NotImplementedError
