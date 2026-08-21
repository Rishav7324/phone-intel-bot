"""Unit tests for HTML escaping, upgraded report formatting, and language templates."""

import pytest
from bot.database.db import AdminStats
from bot.services.formatter import (
    escape,
    format_about_message,
    format_admin_stats,
    format_batch_report,
    format_country_report,
    format_help_message,
    format_lookup_report,
    format_privacy_message,
    format_rate_limit_message,
    format_start_message,
)
from bot.services.providers.base import NumberStatus, PhoneMetadata
from bot.utils.country_data import CountryInfo


def test_escape_html_entities():
    """Verify that HTML special characters are properly escaped."""
    assert escape("<script>alert('xss')</script>") == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    assert escape("AT&T & Verizon") == "AT&amp;T &amp; Verizon"
    assert escape(None) == ""


def test_format_lookup_report_valid():
    """Test report generation for a valid phone number with enriched attributes."""
    meta = PhoneMetadata(
        input_number="+919876543210",
        status=NumberStatus.VALID,
        is_valid=True,
        is_possible=True,
        country_code=91,
        country_calling_code_str="+91",
        region_code="IN",
        country_name="India",
        flag_emoji="🇮🇳",
        number_type="Mobile",
        carrier="Airtel",
        region_description="India",
        timezones=["Asia/Calcutta"],
        risk_level="🟢 Low",
        risk_description="Standard cellular range",
        capital="New Delhi",
        currency="INR (₹)",
        e164_format="+919876543210",
        international_format="+91 98765 43210",
        national_format="09876543210",
    )
    report_en = format_lookup_report(meta, lang="en")
    assert "PHONE LOOKUP REPORT" in report_en
    assert "🇮🇳" in report_en
    assert "+91 98765 43210" in report_en
    assert "India" in report_en
    assert "+91" in report_en
    assert "Mobile" in report_en
    assert "Risk Assessment" in report_en
    assert "New Delhi" in report_en

    report_hi = format_lookup_report(meta, lang="hi")
    assert "फोन नंबर इंटेलिजेंस रिपोर्ट" in report_hi
    assert "🇮🇳" in report_hi
    assert "भारत" in report_hi or "India" in report_hi
    assert "ऑपरेटर" in report_hi


def test_format_country_report():
    """Test country dial code profile report."""
    info = CountryInfo("Japan", "जापान", "JP", "JPN", "+81", "🇯🇵", "Tokyo", "JPY (¥)", "Japanese")
    res = format_country_report(info)
    assert "🇯🇵" in res
    assert "Japan" in res
    assert "+81" in res
    assert "Tokyo" in res


def test_format_batch_report():
    """Test batch analysis summary."""
    meta1 = PhoneMetadata(input_number="+919876543210", status=NumberStatus.VALID, is_valid=True, is_possible=True, country_name="India", flag_emoji="🇮🇳", number_type="Mobile", e164_format="+919876543210")
    meta2 = PhoneMetadata(input_number="12345", status=NumberStatus.INVALID, is_valid=False, is_possible=False, country_name="Unknown", flag_emoji="🌐", number_type="Unknown")

    batch_text = format_batch_report([meta1, meta2], lang="en")
    assert "BATCH LOOKUP REPORT (2 Numbers)" in batch_text
    assert "1/2 Valid Formats" in batch_text


def test_format_standard_messages():
    """Test standard bot response screens in English and Hindi."""
    start_en = format_start_message("en")
    assert "Phone Intelligence Bot" in start_en

    start_hi = format_start_message("hi")
    assert "फोन इंटेलिजेंस बॉट" in start_hi

    help_msg = format_help_message("en")
    assert "/country" in help_msg
    assert "/batch" in help_msg

    privacy_msg = format_privacy_message()
    assert "Zero Raw Number Storage" in privacy_msg

    about_msg = format_about_message()
    assert "libphonenumber" in about_msg

    rate_msg = format_rate_limit_message(30)
    assert "30 seconds" in rate_msg
