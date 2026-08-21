"""Input validation and sanitization for phone numbers."""

import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

# Maximum allowed character length for phone number queries to prevent abuse
MAX_INPUT_LENGTH = 50

# Minimum digit count for a potentially valid phone number
MIN_DIGITS = 4
MAX_DIGITS = 17

# Permissible characters in a raw phone query: digits, +, spaces, hyphens, periods, parentheses
ALLOWED_CHAR_PATTERN = re.compile(r"^[0-9+\s\-(). extExt#]+$")


@dataclass
class ValidationResult:
    """Result of preliminary phone input validation."""
    is_valid_format: bool
    sanitized_input: str
    error_message: Optional[str] = None
    has_plus_prefix: bool = False
    digit_count: int = 0


def sanitize_input(raw_text: str) -> str:
    """Normalize unicode characters and strip excessive whitespace."""
    if not raw_text:
        return ""
    # Normalize unicode (NFKC) to resolve full-width characters, zero-width spaces, etc.
    normalized = unicodedata.normalize("NFKC", raw_text)
    # Remove control characters
    cleaned = "".join(ch for ch in normalized if unicodedata.category(ch)[0] != "C")
    return cleaned.strip()


def validate_phone_input(raw_input: str) -> ValidationResult:
    """Validate user input before attempting library parsing.

    Checks:
    - Empty or whitespace-only input
    - Maximum input length
    - Allowed character set
    - Digit count boundaries
    - Detects whether an international '+' prefix is present
    """
    if not raw_input:
        return ValidationResult(
            is_valid_format=False,
            sanitized_input="",
            error_message="Input is empty. Please provide a phone number."
        )

    sanitized = sanitize_input(raw_input)

    if not sanitized:
        return ValidationResult(
            is_valid_format=False,
            sanitized_input="",
            error_message="Input is empty or contains only non-printable characters."
        )

    if len(sanitized) > MAX_INPUT_LENGTH:
        return ValidationResult(
            is_valid_format=False,
            sanitized_input=sanitized[:MAX_INPUT_LENGTH],
            error_message=f"Input exceeds maximum allowed length of {MAX_INPUT_LENGTH} characters."
        )

    # Check for invalid mixed letters or unsupported symbols
    if not ALLOWED_CHAR_PATTERN.match(sanitized):
        return ValidationResult(
            is_valid_format=False,
            sanitized_input=sanitized,
            error_message="Input contains invalid characters. Only digits, +, spaces, hyphens, and parentheses are supported."
        )

    # Count digits
    digits = [c for c in sanitized if c.isdigit()]
    digit_count = len(digits)

    if digit_count < MIN_DIGITS:
        return ValidationResult(
            is_valid_format=False,
            sanitized_input=sanitized,
            error_message=f"Number is too short (found {digit_count} digits, minimum is {MIN_DIGITS}).",
            digit_count=digit_count
        )

    if digit_count > MAX_DIGITS:
        return ValidationResult(
            is_valid_format=False,
            sanitized_input=sanitized,
            error_message=f"Number is too long (found {digit_count} digits, maximum is {MAX_DIGITS}).",
            digit_count=digit_count
        )

    has_plus = sanitized.startswith("+")

    return ValidationResult(
        is_valid_format=True,
        sanitized_input=sanitized,
        error_message=None,
        has_plus_prefix=has_plus,
        digit_count=digit_count
    )
