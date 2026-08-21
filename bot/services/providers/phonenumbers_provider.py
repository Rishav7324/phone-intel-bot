"""Local metadata provider leveraging Google's libphonenumber via phonenumbers."""

import logging
import re
from typing import Dict, List, Optional
import phonenumbers
from phonenumbers import carrier, geocoder, timezone, PhoneNumberType, NumberParseException

from bot.utils.country_data import COUNTRY_DIRECTORY, get_flag_emoji
from .base import NumberStatus, PhoneLookupProvider, PhoneMetadata

logger = logging.getLogger(__name__)

# Mapping from PhoneNumberType enum values to human-readable strings
NUMBER_TYPE_MAPPING: Dict[int, str] = {
    PhoneNumberType.MOBILE: "Mobile",
    PhoneNumberType.FIXED_LINE: "Landline / Fixed Line",
    PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
    PhoneNumberType.VOIP: "VoIP (Voice over IP)",
    PhoneNumberType.TOLL_FREE: "Toll Free",
    PhoneNumberType.PREMIUM_RATE: "Premium Rate",
    PhoneNumberType.SHARED_COST: "Shared Cost",
    PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
    PhoneNumberType.PAGER: "Pager",
    PhoneNumberType.UAN: "Universal Access Number (UAN)",
    PhoneNumberType.VOICEMAIL: "Voicemail",
    PhoneNumberType.UNKNOWN: "Unknown",
}


def assess_risk(number_type: int) -> tuple[str, str]:
    """Calculate telecom risk level based on allocation type."""
    if number_type == PhoneNumberType.PREMIUM_RATE:
        return "🔴 High", "Premium rate billing range (Potential toll/spam risk)"
    elif number_type == PhoneNumberType.VOIP:
        return "🟡 Medium", "VoIP / Virtual number (Often used for temporary OTP/burners)"
    elif number_type == PhoneNumberType.SHARED_COST:
        return "🟡 Medium", "Shared cost telephone service"
    elif number_type == PhoneNumberType.TOLL_FREE:
        return "🟢 Low", "Toll-free business range"
    elif number_type in (PhoneNumberType.MOBILE, PhoneNumberType.FIXED_LINE, PhoneNumberType.FIXED_LINE_OR_MOBILE):
        return "🟢 Low", "Standard telecom subscriber range"
    return "⚪ Neutral", "Unclassified number range"


class PhonenumbersProvider(PhoneLookupProvider):
    """Offline phone metadata provider using the standard phonenumbers library."""

    async def lookup(
        self,
        phone_number: str,
        default_region: Optional[str] = None
    ) -> PhoneMetadata:
        """Parse and extract metadata using phonenumbers."""
        cleaned_input = phone_number.strip()
        used_default = False

        # Attempt to parse phone number
        try:
            if not cleaned_input.startswith("+") and default_region:
                parsed_num = phonenumbers.parse(cleaned_input, default_region.upper())
                used_default = True
            else:
                parsed_num = phonenumbers.parse(cleaned_input, None)
        except NumberParseException as e:
            logger.debug("NumberParseException on '%s': %s", cleaned_input, e)
            error_text = self._map_parse_error(e.error_type)
            return PhoneMetadata(
                input_number=cleaned_input,
                status=NumberStatus.INVALID,
                is_valid=False,
                is_possible=False,
                error_message=error_text,
            )
        except Exception as e:
            logger.error("Unexpected error during parsing: %s", e)
            return PhoneMetadata(
                input_number=cleaned_input,
                status=NumberStatus.INVALID,
                is_valid=False,
                is_possible=False,
                error_message="Could not parse number due to an internal formatting error.",
            )

        # Validation checks
        is_possible = phonenumbers.is_possible_number(parsed_num)
        is_valid = phonenumbers.is_valid_number(parsed_num)

        # Status determination
        if is_valid:
            status = NumberStatus.VALID
        elif is_possible:
            status = NumberStatus.POSSIBLE
        else:
            status = NumberStatus.INVALID

        # Formats
        e164_str = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.E164)
        intl_str = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        natl_str = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.NATIONAL)
        rfc3966_str = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.RFC3966)

        # Country Calling Code & Region
        country_calling_code = parsed_num.country_code
        calling_code_str = f"+{country_calling_code}" if country_calling_code else None
        region_iso = phonenumbers.region_code_for_number(parsed_num)

        # Flag and Country Details
        flag = get_flag_emoji(region_iso)
        country_profile = COUNTRY_DIRECTORY.get(region_iso) if region_iso else None
        capital = country_profile.capital if country_profile else None
        currency = country_profile.currency if country_profile else None

        # Country / Location description
        country_name = geocoder.country_name_for_number(parsed_num, "en") or "Not available"
        region_desc = geocoder.description_for_number(parsed_num, "en") or "Not available"

        # Carrier
        carrier_name = carrier.name_for_number(parsed_num, "en")
        carrier_str = carrier_name if carrier_name else "Not available"

        # Number type & risk
        num_type_enum = phonenumbers.number_type(parsed_num)
        num_type_str = NUMBER_TYPE_MAPPING.get(num_type_enum, "Unknown")
        risk_level, risk_desc = assess_risk(num_type_enum)

        # Emergency check
        is_emergency = False
        try:
            if region_iso:
                is_emergency = phonenumbers.is_emergency_number(cleaned_input, region_iso)
        except Exception:
            pass

        # Timezones
        tz_tuple = timezone.time_zones_for_number(parsed_num)
        timezones_list: List[str] = list(tz_tuple) if tz_tuple else ["Not available"]

        # Direct Chat links (only for valid/possible numbers)
        digits_only = re.sub(r"\D", "", e164_str) if e164_str else ""
        wa_link = f"https://wa.me/{digits_only}" if digits_only else None
        tg_link = f"https://t.me/+{digits_only}" if digits_only else None

        return PhoneMetadata(
            input_number=cleaned_input,
            status=status,
            is_valid=is_valid,
            is_possible=is_possible,
            is_emergency=is_emergency,
            country_code=country_calling_code,
            country_calling_code_str=calling_code_str,
            region_code=region_iso,
            country_name=country_name if country_name != "Not available" else region_desc,
            flag_emoji=flag,
            number_type=num_type_str,
            carrier=carrier_str,
            region_description=region_desc,
            timezones=timezones_list,
            risk_level=risk_level,
            risk_description=risk_desc,
            e164_format=e164_str,
            international_format=intl_str,
            national_format=natl_str,
            rfc3966_format=rfc3966_str,
            capital=capital,
            currency=currency,
            wa_link=wa_link,
            tg_link=tg_link,
            used_default_region=used_default,
        )

    def _map_parse_error(self, error_type: int) -> str:
        """Translate phonenumbers NumberParseException error types into user-friendly messages."""
        if error_type == NumberParseException.INVALID_COUNTRY_CODE:
            return (
                "Missing or invalid country code.\n\n"
                "Please include the country calling code with '+' prefix, "
                "e.g., <code>+91 98765 43210</code> or <code>+1 202 555 0123</code>."
            )
        elif error_type == NumberParseException.NOT_A_NUMBER:
            return "The provided text is not recognized as a telephone number."
        elif error_type == NumberParseException.TOO_SHORT_NSN:
            return "The number is too short after the country code."
        elif error_type == NumberParseException.TOO_LONG:
            return "The number exceeds the maximum valid telephone length."
        elif error_type == NumberParseException.TOO_SHORT_AFTER_IDD:
            return "The number is too short after the international direct dialing prefix."
        return "Invalid telephone number format."
