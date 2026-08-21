"""Phone lookup service orchestrating provider execution and caching."""

import logging
from typing import Optional
from bot.services.cache import MemoryCache
from bot.services.providers.base import NumberStatus, PhoneLookupProvider, PhoneMetadata
from bot.services.providers.phonenumbers_provider import PhonenumbersProvider
from bot.utils.validators import validate_phone_input

logger = logging.getLogger(__name__)


class PhoneLookupService:
    """High-level phone intelligence service coordinating caching and provider lookups."""

    def __init__(
        self,
        provider: Optional[PhoneLookupProvider] = None,
        cache: Optional[MemoryCache] = None,
    ):
        self.provider: PhoneLookupProvider = provider or PhonenumbersProvider()
        self.cache: MemoryCache = cache or MemoryCache()

    async def lookup(
        self,
        raw_phone_number: str,
        default_region: Optional[str] = None
    ) -> PhoneMetadata:
        """Validate, check cache, and perform lookup for a phone number."""
        # 1. Input format & length validation
        validation = validate_phone_input(raw_phone_number)
        if not validation.is_valid_format:
            logger.debug("Validation failed for input: %s", validation.error_message)
            return PhoneMetadata(
                input_number=validation.sanitized_input or raw_phone_number,
                status=NumberStatus.INVALID,
                is_valid=False,
                is_possible=False,
                error_message=validation.error_message,
            )

        sanitized_number = validation.sanitized_input

        # 2. Check cache (use sanitized number + default region as key)
        cache_key = f"{sanitized_number}:{default_region or 'NONE'}"
        cached_result = await self.cache.get(cache_key)
        if cached_result is not None:
            logger.debug("Cache hit for lookup query: %s", sanitized_number)
            return cached_result

        # 3. Perform provider lookup
        metadata = await self.provider.lookup(
            phone_number=sanitized_number,
            default_region=default_region
        )

        # 4. Cache valid / possible results for performance
        if metadata.status in (NumberStatus.VALID, NumberStatus.POSSIBLE):
            await self.cache.set(cache_key, metadata)
            # Also cache by E.164 if available
            if metadata.e164_format and metadata.e164_format != cache_key:
                await self.cache.set(f"{metadata.e164_format}:{default_region or 'NONE'}", metadata)

        return metadata
