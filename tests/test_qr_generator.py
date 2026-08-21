"""Unit tests for QR code and vCard contact card generator."""

from bot.services.providers.base import NumberStatus, PhoneMetadata
from bot.utils.qr_generator import generate_contact_qr, generate_vcard


def test_generate_contact_qr():
    """Verify PNG QR code generation with valid PNG header."""
    qr_bio = generate_contact_qr("+919876543210")
    data = qr_bio.getvalue()
    assert len(data) > 0
    # PNG Magic Header
    assert data.startswith(b"\x89PNG\r\n\x1a\n")


def test_generate_vcard():
    """Verify RFC 6350 vCard formatting."""
    meta = PhoneMetadata(
        input_number="+919876543210",
        status=NumberStatus.VALID,
        is_valid=True,
        country_name="India",
        flag_emoji="🇮🇳",
        number_type="Mobile",
        carrier="Airtel",
        e164_format="+919876543210",
        international_format="+91 98765 43210",
    )
    vcf_bio = generate_vcard(meta)
    vcf_str = vcf_bio.getvalue().decode("utf-8")

    assert "BEGIN:VCARD" in vcf_str
    assert "VERSION:3.0" in vcf_str
    assert "+919876543210" in vcf_str
    assert "India" in vcf_str
    assert "END:VCARD" in vcf_str
