"""Unit and integration tests for PhoneLookupService and PhonenumbersProvider."""

import pytest
from bot.services.cache import MemoryCache
from bot.services.phone_lookup import PhoneLookupService
from bot.services.providers.base import NumberStatus
from bot.services.providers.phonenumbers_provider import PhonenumbersProvider


@pytest.fixture
def lookup_service():
    """Fixture providing a fresh PhoneLookupService instance."""
    provider = PhonenumbersProvider()
    cache = MemoryCache(default_ttl=600)
    return PhoneLookupService(provider=provider, cache=cache)


@pytest.mark.asyncio
async def test_valid_indian_number(lookup_service):
    """Test lookup of an Indian phone number format."""
    # +91 98765 43210 is a standard possible Indian mobile number
    metadata = await lookup_service.lookup("+919876543210")

    assert metadata.status in (NumberStatus.VALID, NumberStatus.POSSIBLE)
    assert metadata.country_code == 91
    assert metadata.country_calling_code_str == "+91"
    assert metadata.region_code == "IN"
    assert "India" in metadata.country_name
    assert metadata.number_type in ("Mobile", "Fixed Line / Mobile")
    assert metadata.e164_format == "+919876543210"
    assert any("Asia/Calcutta" in tz or "Asia/Kolkata" in tz for tz in metadata.timezones)


@pytest.mark.asyncio
async def test_valid_us_number(lookup_service):
    """Test lookup of a standard United States phone number."""
    # Official sample/test number format in US (e.g. Googleplex +1 650 253 0000)
    metadata = await lookup_service.lookup("+1 650 253 0000")

    assert metadata.status == NumberStatus.VALID
    assert metadata.country_code == 1
    assert metadata.country_calling_code_str == "+1"
    assert metadata.region_code == "US"
    assert "United States" in metadata.country_name or "California" in metadata.region_description
    assert metadata.e164_format == "+16502530000"
    assert metadata.international_format == "+1 650-253-0000"


@pytest.mark.asyncio
async def test_valid_uk_number(lookup_service):
    """Test lookup of an official UK drama/sample number (+44 20 7946 0958)."""
    metadata = await lookup_service.lookup("+44 20 7946 0958")

    assert metadata.status in (NumberStatus.VALID, NumberStatus.POSSIBLE)
    assert metadata.country_code == 44
    assert metadata.country_calling_code_str == "+44"
    assert metadata.region_code == "GB"
    assert "United Kingdom" in metadata.country_name or "London" in metadata.region_description


@pytest.mark.asyncio
async def test_missing_country_code_without_default_region(lookup_service):
    """Test that submitting a number without '+' or country code returns an informative error."""
    metadata = await lookup_service.lookup("9876543210", default_region=None)

    assert metadata.status == NumberStatus.INVALID
    assert metadata.is_valid is False
    assert metadata.error_message is not None
    assert "country code" in metadata.error_message.lower()


@pytest.mark.asyncio
async def test_missing_country_code_with_default_region(lookup_service):
    """Test that default region fallback parses successfully when configured."""
    metadata = await lookup_service.lookup("9876543210", default_region="IN")

    assert metadata.status in (NumberStatus.VALID, NumberStatus.POSSIBLE)
    assert metadata.region_code == "IN"
    assert metadata.country_code == 91
    assert metadata.used_default_region is True


@pytest.mark.asyncio
async def test_invalid_and_malformed_numbers(lookup_service):
    """Test handling of invalid and malformed phone inputs."""
    # Completely invalid digits
    meta1 = await lookup_service.lookup("+99999999999999")
    assert meta1.status == NumberStatus.INVALID
    assert meta1.is_valid is False

    # Too short
    meta2 = await lookup_service.lookup("+1 23")
    assert meta2.status == NumberStatus.INVALID


@pytest.mark.asyncio
async def test_toll_free_and_special_number_types(lookup_service):
    """Test identification of Toll Free and special number types."""
    # US Toll Free format: +1 800 225 5288
    metadata = await lookup_service.lookup("+1 800 225 5288")
    assert metadata.status == NumberStatus.VALID
    assert metadata.number_type == "Toll Free"


@pytest.mark.asyncio
async def test_caching_behavior(lookup_service):
    """Test that repeated lookups hit the in-memory cache."""
    num = "+1 650 253 0000"

    # First lookup (uncached)
    res1 = await lookup_service.lookup(num)
    assert res1.status == NumberStatus.VALID

    # Check cache directly
    cached = await lookup_service.cache.get(f"{num}:NONE")
    assert cached is not None
    assert cached.e164_format == res1.e164_format

    # Second lookup should return cached object
    res2 = await lookup_service.lookup(num)
    assert res2.e164_format == res1.e164_format
