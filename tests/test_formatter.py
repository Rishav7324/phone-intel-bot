"""Unit tests for HTML escaping and response formatting."""

import pytest
from bot.database.db import AdminStats
from bot.services.formatter import (
    escape,
    format_about_message,
    format_admin_stats,
    format_help_message,
    format_lookup_report,
    format_privacy_message,
    format_rate_limit_message,
    format_start_message,
)
from bot.services.providers.base import NumberStatus, PhoneMetadata


def test_escape_html_entities():
    """Verify that HTML special characters are properly escaped."""
    assert escape("<script>alert('xss')</script>") == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    assert escape("AT&T & Verizon") == "AT&amp;T &amp; Verizon"
    assert escape(None) == ""


def test_format_lookup_report_valid():
    """Test report generation for a valid phone number."""
    meta = PhoneMetadata(
        input_number="+919876543210",
        status=NumberStatus.VALID,
        is_valid=True,
        is_possible=True,
        country_code=91,
        country_calling_code_str="+91",
        region_code="IN",
        country_name="India",
        number_type="Mobile",
        carrier="Airtel",
        region_description="India",
        timezones=["Asia/Calcutta"],
        e164_format="+919876543210",
        international_format="+91 98765 43210",
        national_format="09876543210",
    )
    report = format_lookup_report(meta)
    assert "PHONE LOOKUP REPORT" in report
    assert "+91 98765 43210" in report
    assert "India" in report
    assert "+91" in report
    assert "Mobile" in report
    assert "Yes (Valid number format)" in report
    assert "Airtel" in report
    assert "Asia/Calcutta" in report
    assert "Public metadata only" in report


def test_format_lookup_report_invalid_with_error():
    """Test report generation for invalid input with specific error message."""
    meta = PhoneMetadata(
        input_number="12345",
        status=NumberStatus.INVALID,
        is_valid=False,
        is_possible=False,
        error_message="Missing or invalid country code.",
    )
    report = format_lookup_report(meta)
    assert "PHONE LOOKUP ERROR" in report
    assert "12345" in report
    assert "Missing or invalid country code" in report


def test_format_admin_stats():
    """Test generation of admin statistics summary."""
    stats = AdminStats(
        total_users=150,
        total_lookups=1200,
        today_lookups=45,
        top_countries=[("IN (+91)", 700), ("US (+1)", 300)],
        valid_lookups=1100,
        invalid_lookups=100,
    )
    res = format_admin_stats(stats)
    assert "BOT SYSTEM & USAGE STATISTICS" in res
    assert "150" in res
    assert "1,200" in res
    assert "45" in res
    assert "IN (+91)" in res
    assert "700" in res
    assert "Zero raw numbers stored" in res


def test_format_standard_messages():
    """Test standard bot response screens."""
    start_msg = format_start_message()
    assert "Phone Intelligence Bot" in start_msg
    assert "+91" in start_msg

    help_msg = format_help_message()
    assert "/start" in help_msg
    assert "Rate Limit" in help_msg

    privacy_msg = format_privacy_message()
    assert "Zero Raw Number Storage" in privacy_msg

    about_msg = format_about_message()
    assert "libphonenumber" in about_msg

    rate_msg = format_rate_limit_message(30)
    assert "30 seconds" in rate_msg
