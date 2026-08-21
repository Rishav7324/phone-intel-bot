"""Unit tests for Multi-Tool suite: IP, DNS, Email, Hashes, Passwords, Base64, JWT, and Forex."""

import pytest
from bot.tools.crypto_tool import (
    convert_color,
    convert_epoch,
    decode_jwt,
    generate_hashes,
    generate_password,
    generate_uuids,
    handle_base64,
)
from bot.tools.domain_tool import lookup_dns
from bot.tools.email_tool import validate_email
from bot.tools.ip_tool import check_port, lookup_ip
from bot.tools.market_tool import convert_currency


@pytest.mark.asyncio
async def test_email_validation():
    """Verify email format, disposable detection, and validation."""
    # Free provider
    res_gmail = await validate_email("user@gmail.com")
    assert res_gmail["is_valid_format"] is True
    assert res_gmail["is_free"] is True
    assert res_gmail["is_disposable"] is False

    # Disposable email
    res_temp = await validate_email("burner@tempmail.com")
    assert res_temp["is_valid_format"] is True
    assert res_temp["is_disposable"] is True
    assert "Disposable" in res_temp["status"]

    # Invalid syntax
    res_inv = await validate_email("invalid@@email..com")
    assert res_inv["is_valid_format"] is False
    assert "Invalid Format" in res_inv["status"]


def test_hash_generation():
    """Verify cryptographic hash generation."""
    hashes = generate_hashes("antigravity")
    assert len(hashes["md5"]) == 32
    assert len(hashes["sha1"]) == 40
    assert len(hashes["sha256"]) == 64
    assert len(hashes["sha512"]) == 128


def test_base64_operations():
    """Verify Base64 encode and decode."""
    ok_enc, enc_val = handle_base64("enc", "Hello World")
    assert ok_enc is True
    assert enc_val == "SGVsbG8gV29ybGQ="

    ok_dec, dec_val = handle_base64("dec", "SGVsbG8gV29ybGQ=")
    assert ok_dec is True
    assert dec_val == "Hello World"


def test_password_generation():
    """Verify high-entropy password generation length and complexity."""
    pwd16 = generate_password(16, include_symbols=True)
    assert len(pwd16) == 16
    assert any(c.isupper() for c in pwd16)
    assert any(c.islower() for c in pwd16)
    assert any(c.isdigit() for c in pwd16)


def test_uuid_generation():
    """Verify UUID generation format."""
    uuids = generate_uuids()
    assert len(uuids["uuid4"]) == 36
    assert len(uuids["hex"]) == 32


def test_jwt_decoder():
    """Verify decoding of a sample JWT token."""
    # Test token: header: {"alg":"HS256","typ":"JWT"}, payload: {"sub":"1234567890","name":"John Doe","iat":1516239022}
    sample_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    res = decode_jwt(sample_jwt)
    assert res["success"] is True
    assert res["algorithm"] == "HS256"
    assert res["payload"]["name"] == "John Doe"


def test_epoch_converter():
    """Verify epoch timestamp conversions."""
    res = convert_epoch("1700000000")
    assert res["epoch"] == 1700000000
    assert "2023" in res["utc_str"]


def test_color_swatch_generator():
    """Verify HEX color conversion and PNG generation."""
    color_info, bio = convert_color("#FF5733")
    assert color_info["hex"] == "#FF5733"
    assert color_info["r"] == 255
    assert color_info["g"] == 87
    assert color_info["b"] == 51
    assert bio.getvalue().startswith(b"\x89PNG\r\n\x1a\n")


@pytest.mark.asyncio
async def test_dns_lookup():
    """Verify DNS record queries."""
    res = await lookup_dns("google.com")
    assert res["success"] is True
    assert len(res["records"]["A"]) > 0


@pytest.mark.asyncio
async def test_port_check():
    """Verify port checking logic."""
    res = await check_port("1.1.1.1", 53)
    assert res["success"] is True


@pytest.mark.asyncio
async def test_find_subdomains():
    """Verify resilient subdomain discovery."""
    from bot.tools.domain_tool import find_subdomains
    res = await find_subdomains("telegram.org")
    assert res["success"] is True
    assert len(res["subdomains"]) > 0

