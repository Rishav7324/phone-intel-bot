"""Unit tests for phone input validation and sanitization."""

import pytest
from bot.utils.validators import validate_phone_input, sanitize_input, MAX_INPUT_LENGTH


def test_sanitize_input():
    """Test unicode normalization and whitespace stripping."""
    assert sanitize_input("  +91 98765 43210  ") == "+91 98765 43210"
    # Zero width space or fullwidth characters
    assert sanitize_input("＋９１９８７６５４３２１０") == "+919876543210"
    assert sanitize_input("") == ""


def test_validate_empty_input():
    """Test validation on empty and whitespace-only inputs."""
    res1 = validate_phone_input("")
    assert not res1.is_valid_format
    assert "empty" in res1.error_message.lower()

    res2 = validate_phone_input("   ")
    assert not res2.is_valid_format
    assert "empty" in res2.error_message.lower()


def test_validate_excessive_length():
    """Test rejection of inputs exceeding maximum allowed length."""
    long_input = "+1" + "9" * (MAX_INPUT_LENGTH + 10)
    res = validate_phone_input(long_input)
    assert not res.is_valid_format
    assert "maximum allowed length" in res.error_message


def test_validate_invalid_characters():
    """Test rejection of letters, emojis, and unauthorized characters."""
    res1 = validate_phone_input("+91 98765 ABCDE")
    assert not res1.is_valid_format
    assert "invalid characters" in res1.error_message.lower()

    res2 = validate_phone_input("+91 98765 📱43210")
    assert not res2.is_valid_format
    assert "invalid characters" in res2.error_message.lower()

    res3 = validate_phone_input("SELECT * FROM users;")
    assert not res3.is_valid_format


def test_validate_digit_count_boundaries():
    """Test bounds on digit counts."""
    # Too short
    res_short = validate_phone_input("+12")
    assert not res_short.is_valid_format
    assert "too short" in res_short.error_message.lower()

    # Too long
    res_long = validate_phone_input("+1234567890123456789")
    assert not res_long.is_valid_format
    assert "too long" in res_long.error_message.lower()


def test_validate_valid_phone_formats():
    """Test valid inputs in various typical phone formatting styles."""
    res1 = validate_phone_input("+91 98765 43210")
    assert res1.is_valid_format
    assert res1.has_plus_prefix
    assert res1.digit_count == 12

    res2 = validate_phone_input("+1 (202) 555-0123")
    assert res2.is_valid_format
    assert res2.has_plus_prefix
    assert res2.digit_count == 11

    res3 = validate_phone_input("9876543210")
    assert res3.is_valid_format
    assert not res3.has_plus_prefix
    assert res3.digit_count == 10
