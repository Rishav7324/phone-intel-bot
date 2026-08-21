"""Country directory and emoji flag utility."""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class CountryInfo:
    """Detailed country profile."""
    name_en: str
    name_hi: str
    iso2: str
    iso3: str
    calling_code: str
    flag: str
    capital: str
    currency: str
    languages: str


def get_flag_emoji(country_code: Optional[str]) -> str:
    """Generate unicode flag emoji from ISO 3166-1 alpha-2 code."""
    if not country_code or len(country_code) != 2:
        return "🌐"
    code = country_code.upper()
    try:
        # Convert 2-letter ISO code to regional indicator symbols
        return "".join(chr(127397 + ord(c)) for c in code)
    except Exception:
        return "🌐"


# Common countries directory for fast enrichment and /country command
COUNTRY_DIRECTORY: Dict[str, CountryInfo] = {
    "IN": CountryInfo("India", "भारत", "IN", "IND", "+91", "🇮🇳", "New Delhi", "INR (₹)", "Hindi, English"),
    "US": CountryInfo("United States", "संयुक्त राज्य अमेरिका", "US", "USA", "+1", "🇺🇸", "Washington, D.C.", "USD ($)", "English"),
    "GB": CountryInfo("United Kingdom", "यूनाइटेड किंगडम", "GB", "GBR", "+44", "🇬🇧", "London", "GBP (£)", "English"),
    "CA": CountryInfo("Canada", "कनाडा", "CA", "CAN", "+1", "🇨🇦", "Ottawa", "CAD ($)", "English, French"),
    "AU": CountryInfo("Australia", "ऑस्ट्रेलिया", "AU", "AUS", "+61", "🇦🇺", "Canberra", "AUD ($)", "English"),
    "DE": CountryInfo("Germany", "जर्मनी", "DE", "DEU", "+49", "🇩🇪", "Berlin", "EUR (€)", "German"),
    "FR": CountryInfo("France", "फ़्रांस", "FR", "FRA", "+33", "🇫🇷", "Paris", "EUR (€)", "French"),
    "AE": CountryInfo("United Arab Emirates", "संयुक्त अरब अमीरात", "AE", "ARE", "+971", "🇦🇪", "Abu Dhabi", "AED (د.إ)", "Arabic"),
    "SA": CountryInfo("Saudi Arabia", "सऊदी अरब", "SA", "SAU", "+966", "🇸🇦", "Riyadh", "SAR (﷼)", "Arabic"),
    "SG": CountryInfo("Singapore", "सिंगापुर", "SG", "SGP", "+65", "🇸🇬", "Singapore", "SGD ($)", "English, Malay, Mandarin, Tamil"),
    "PK": CountryInfo("Pakistan", "पाकिस्तान", "PK", "PAK", "+92", "🇵🇰", "Islamabad", "PKR (₨)", "Urdu, English"),
    "BD": CountryInfo("Bangladesh", "बांग्लादेश", "BD", "BGD", "+880", "🇧🇩", "Dhaka", "BDT (৳)", "Bengali"),
    "NP": CountryInfo("Nepal", "नेपाल", "NP", "NPL", "+977", "🇳🇵", "Kathmandu", "NPR (₨)", "Nepali"),
    "LK": CountryInfo("Sri Lanka", "श्रीलंका", "LK", "LKA", "+94", "🇱🇰", "Sri Jayawardenepura Kotte", "LKR (Rs)", "Sinhala, Tamil"),
    "RU": CountryInfo("Russia", "रूस", "RU", "RUS", "+7", "🇷🇺", "Moscow", "RUB (₽)", "Russian"),
    "CN": CountryInfo("China", "चीन", "CN", "CHN", "+86", "🇨🇳", "Beijing", "CNY (¥)", "Mandarin"),
    "JP": CountryInfo("Japan", "जापान", "JP", "JPN", "+81", "🇯🇵", "Tokyo", "JPY (¥)", "Japanese"),
    "BR": CountryInfo("Brazil", "ब्राजील", "BR", "BRA", "+55", "🇧🇷", "Brasília", "BRL (R$)", "Portuguese"),
    "ZA": CountryInfo("South Africa", "दक्षिण अफ्रीका", "ZA", "ZAF", "+27", "🇿🇦", "Pretoria", "ZAR (R)", "11 official languages"),
    "NG": CountryInfo("Nigeria", "नाइजीरिया", "NG", "NGA", "+234", "🇳🇬", "Abuja", "NGN (₦)", "English"),
    "MY": CountryInfo("Malaysia", "मलेशिया", "MY", "MYS", "+60", "🇲🇾", "Kuala Lumpur", "MYR (RM)", "Malay"),
    "ID": CountryInfo("Indonesia", "इंडोनेशिया", "ID", "IDN", "+62", "🇮🇩", "Jakarta", "IDR (Rp)", "Indonesian"),
    "PH": CountryInfo("Philippines", "फ़िलीपींस", "PH", "PHL", "+63", "🇵🇭", "Manila", "PHP (₱)", "Filipino, English"),
    "TR": CountryInfo("Turkey", "तुर्की", "TR", "TUR", "+90", "🇹🇷", "Ankara", "TRY (₺)", "Turkish"),
    "IT": CountryInfo("Italy", "इटली", "IT", "ITA", "+39", "🇮🇹", "Rome", "EUR (€)", "Italian"),
    "ES": CountryInfo("Spain", "स्पेन", "ES", "ESP", "+34", "🇪🇸", "Madrid", "EUR (€)", "Spanish"),
    "NL": CountryInfo("Netherlands", "नीदरलैंड", "NL", "NLD", "+31", "🇳🇱", "Amsterdam", "EUR (€)", "Dutch"),
    "CH": CountryInfo("Switzerland", "स्विट्जरलैंड", "CH", "CHE", "+41", "🇨🇭", "Bern", "CHF (CHF)", "German, French, Italian, Romansh"),
    "SE": CountryInfo("Sweden", "स्वीडन", "SE", "SWE", "+46", "🇸🇪", "Stockholm", "SEK (kr)", "Swedish"),
    "NZ": CountryInfo("New Zealand", "न्यूजीलैंड", "NZ", "NZL", "+64", "🇳🇿", "Wellington", "NZD ($)", "English, Māori"),
}


def search_country(query: str) -> Optional[CountryInfo]:
    """Search for country information by name, ISO code, or dialling prefix."""
    q = query.strip().upper().lstrip("+")
    if not q:
        return None

    # Search by ISO 2 code
    if q in COUNTRY_DIRECTORY:
        return COUNTRY_DIRECTORY[q]

    # Search by calling code or name
    for iso2, info in COUNTRY_DIRECTORY.items():
        if info.calling_code.lstrip("+") == q:
            return info
        if info.iso3 == q:
            return info
        if q.lower() in info.name_en.lower() or q in info.name_hi:
            return info

    return None
