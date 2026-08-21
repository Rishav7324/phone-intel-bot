"""Email verification tool: syntax validation, MX servers, and disposable burner detection."""

import asyncio
import re
from typing import Dict, Any, List
import dns.resolver

EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
)

# Common disposable and temporary email domains
DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
    "sharklasers.com", "guerrillamailblock.com", "trashmail.com", "yopmail.com",
    "dispostable.com", "getairmail.com", "throwawaymail.com", "fakeinbox.com",
    "temp-mail.org", "mohmal.com", "crazymailing.com", "mytemp.email",
    "burnermail.io", "maildrop.cc", "nada.ltd", "generator.email",
    "emailondeck.com", "dropmail.me", "fakemailgenerator.com", "trashmail.net",
}

# Free consumer email providers
FREE_PROVIDERS = {
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com",
    "aol.com", "zoho.com", "protonmail.com", "proton.me", "gmx.com", "yandex.com",
}


async def validate_email(email_address: str) -> Dict[str, Any]:
    """Validate email format, MX server records, and disposable email status."""
    email = email_address.strip().lower()

    if not EMAIL_REGEX.match(email):
        return {
            "success": True,
            "email": email,
            "is_valid_format": False,
            "status": "🔴 Invalid Format",
            "reason": "Email does not adhere to RFC 5322 syntax.",
            "has_mx": False,
            "is_disposable": False,
            "domain": "",
            "mx_records": [],
        }

    user_part, domain_part = email.split("@", 1)
    is_disposable = domain_part in DISPOSABLE_DOMAINS
    is_free = domain_part in FREE_PROVIDERS

    # Check MX records via DNS
    loop = asyncio.get_running_loop()

    def _get_mx() -> List[str]:
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 3.0
            resolver.lifetime = 3.0
            answers = resolver.resolve(domain_part, "MX")
            return sorted([str(r.exchange).rstrip(".") for r in answers])
        except Exception:
            return []

    mx_records = await loop.run_in_executor(None, _get_mx)
    has_mx = len(mx_records) > 0

    if is_disposable:
        status = "🟡 High Risk (Disposable / Burner Email)"
        reason = "This address belongs to a temporary or burner disposable email provider."
    elif not has_mx:
        status = "🔴 Undeliverable (No MX Records)"
        reason = f"The domain '{domain_part}' has no mail exchanger (MX) records configured."
    elif is_free:
        status = "🟢 Valid (Free Consumer Mailbox)"
        reason = "Valid mailbox on a recognized public email provider (e.g. Google, Microsoft, Apple)."
    else:
        status = "🟢 Valid (Custom Corporate Domain)"
        reason = f"Valid mailbox hosted on business domain '{domain_part}'."

    return {
        "success": True,
        "email": email,
        "user": user_part,
        "domain": domain_part,
        "is_valid_format": True,
        "status": status,
        "reason": reason,
        "has_mx": has_mx,
        "is_disposable": is_disposable,
        "is_free": is_free,
        "mx_records": mx_records,
    }
