"""Telegram HTML formatting helpers for reports, help screens, and administrative stats."""

import html
from typing import Optional
from bot.database.db import AdminStats
from bot.services.providers.base import NumberStatus, PhoneMetadata


def escape(text: Optional[str]) -> str:
    """Safely escape HTML entities in user-controlled or metadata strings."""
    if text is None:
        return ""
    return html.escape(str(text))


def format_lookup_report(metadata: PhoneMetadata) -> str:
    """Format structured phone metadata into a polished Telegram HTML report."""
    if metadata.status == NumberStatus.INVALID and metadata.error_message:
        return (
            "🔴 <b>PHONE LOOKUP ERROR</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🔢 <b>Input:</b> <code>{escape(metadata.input_number)}</code>\n\n"
            f"⚠️ <b>Reason:</b>\n{escape(metadata.error_message)}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "💡 <i>Tip: Always include the '+' sign and country calling code (e.g. <code>+919876543210</code> or <code>+12025550123</code>).</i>"
        )

    # Valid status icon and text
    if metadata.status == NumberStatus.VALID:
        valid_str = "✅ Yes (Valid number format)"
    elif metadata.status == NumberStatus.POSSIBLE:
        valid_str = "🟡 Possible but unverified"
    else:
        valid_str = "🔴 No (Invalid format)"

    possible_str = "✅ Yes" if metadata.is_possible else "🔴 No"
    display_num = metadata.international_format or metadata.e164_format or metadata.input_number
    calling_code = metadata.country_calling_code_str or (f"+{metadata.country_code}" if metadata.country_code else "Not available")
    timezones_str = ", ".join(metadata.timezones) if metadata.timezones else "Not available"

    lines = [
        "📱 <b>PHONE LOOKUP REPORT</b>",
        "━━━━━━━━━━━━━━━━━━\n",
        f"🔢 <b>Number</b>\n<code>{escape(display_num)}</code>\n",
        f"🌍 <b>Country</b>\n{escape(metadata.country_name)}\n",
        f"📞 <b>Country Code</b>\n{escape(calling_code)}\n",
        f"📱 <b>Type</b>\n{escape(metadata.number_type)}\n",
        f"✅ <b>Valid Format</b>\n{valid_str}\n",
        f"🔎 <b>Possible</b>\n{possible_str}\n",
        f"🏢 <b>Carrier</b>\n{escape(metadata.carrier)}\n",
        f"📍 <b>General Region</b>\n{escape(metadata.region_description)}\n",
        f"🕐 <b>Timezone</b>\n{escape(timezones_str)}\n",
        f"🌐 <b>International</b>\n<code>{escape(metadata.international_format or 'Not available')}</code>\n",
        f"☎️ <b>National</b>\n<code>{escape(metadata.national_format or 'Not available')}</code>\n",
        "━━━━━━━━━━━━━━━━━━",
        "ℹ️ <i>Public metadata only • Not proof of ownership or live status</i>"
    ]

    if metadata.used_default_region:
        lines.append("\n⚠️ <i>Parsed using default region setting.</i>")

    return "\n".join(lines)


def format_start_message() -> str:
    """Return welcome message for /start command."""
    return (
        "📱 <b>Phone Intelligence Bot</b>\n\n"
        "Send me a phone number and I'll check its available public metadata.\n\n"
        "<b>Examples:</b>\n"
        "• <code>+91 98765 43210</code>\n"
        "• <code>+1 202 555 0123</code>\n"
        "• <code>+44 20 7946 0958</code>\n\n"
        "<b>I can provide:</b>\n"
        "• Format validity & possibility\n"
        "• Country & calling code\n"
        "• Number classification (Mobile, Landline, VoIP, etc.)\n"
        "• Carrier metadata\n"
        "• Regional/geographical description\n"
        "• Timezone(s)\n"
        "• Standardized International & National formats\n\n"
        "🔒 <b>Privacy Notice:</b>\n"
        "I do <b>not</b> identify or expose private individual data (names, home addresses, live locations, SMS/calls, or KYC data).\n\n"
        "Type /help for full guide or click <b>🔍 Check Number</b> below!"
    )


def format_help_message() -> str:
    """Return documentation message for /help command."""
    return (
        "📖 <b>Phone Intelligence Bot — Help & Usage Guide</b>\n\n"
        "<b>How to use:</b>\n"
        "Simply send any telephone number in international format.\n\n"
        "<b>Supported Formats:</b>\n"
        "• <code>+919876543210</code> (Compact)\n"
        "• <code>+1 (202) 555-0123</code> (Formatted with brackets/hyphens)\n"
        "• <code>+44 20 7946 0958</code> (Spaced international)\n\n"
        "<b>Available Commands:</b>\n"
        "• /start — Welcome message & quick start\n"
        "• /help — This usage guide\n"
        "• /privacy — Privacy principles & data handling\n"
        "• /about — System architecture and info\n\n"
        "<b>Important Metadata Rules:</b>\n"
        "• <i>Valid</i> format does <b>not</b> mean the number is currently active or in service.\n"
        "• <i>Carrier</i> indicates the original assigned range or network prefix, not current SIM ownership.\n"
        "• <i>Region</i> indicates the telephone prefix area, not live GPS location.\n\n"
        "<b>Rate Limit:</b>\n"
        "Standard limit is 10 lookups per minute per user."
    )


def format_privacy_message() -> str:
    """Return privacy policy for /privacy command."""
    return (
        "🔒 <b>Privacy Policy & Data Principles</b>\n\n"
        "This bot is designed strictly around <b>privacy-by-design</b> principles:\n\n"
        "1. <b>Zero Raw Number Storage:</b>\n"
        "We never save, store, or log raw phone numbers in our database or application logs.\n\n"
        "2. <b>Anonymous Telemetry:</b>\n"
        "Usage statistics only capture anonymous aggregates (timestamp, country code, validity boolean) for load balancing and reporting.\n\n"
        "3. <b>No Private Data Access:</b>\n"
        "This bot does not query government databases, SIM KYC registries, WhatsApp/Telegram accounts, or personal address books.\n\n"
        "4. <b>Log Redaction:</b>\n"
        "All server logs automatically mask phone numbers (e.g. <code>+91******3210</code>) to protect queries."
    )


def format_about_message() -> str:
    """Return bot architecture and technology info for /about command."""
    return (
        "ℹ️ <b>About Phone Intelligence Bot</b>\n\n"
        "A fast, secure, and production-grade Telegram bot providing public telephone number metadata.\n\n"
        "<b>Tech Stack:</b>\n"
        "• Python 3.12+\n"
        "• python-telegram-bot (Async v21+)\n"
        "• Google's libphonenumber (phonenumbers)\n"
        "• Pydantic v2 & Settings\n"
        "• aiosqlite (Async SQLite)\n"
        "• In-Memory TTL Cache\n\n"
        "<b>Security Features:</b>\n"
        "• Per-user sliding window rate limiting\n"
        "• Input length & regex sanitization\n"
        "• Server-side phone number masking\n"
        "• Full HTML injection prevention"
    )


def format_admin_stats(stats: AdminStats) -> str:
    """Return formatted admin statistics report."""
    top_countries_text = ""
    if stats.top_countries:
        for idx, (country, count) in enumerate(stats.top_countries, start=1):
            top_countries_text += f"\n  {idx}. <code>{escape(country)}</code>: {count:,}"
    else:
        top_countries_text = "\n  <i>No lookups recorded yet.</i>"

    return (
        "📊 <b>BOT SYSTEM & USAGE STATISTICS</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>Total Unique Users:</b> {stats.total_users:,}\n"
        f"🔍 <b>Total Lookups:</b> {stats.total_lookups:,}\n"
        f"📅 <b>Today's Lookups:</b> {stats.today_lookups:,}\n"
        f"✅ <b>Valid Lookups:</b> {stats.valid_lookups:,}\n"
        f"❌ <b>Invalid Lookups:</b> {stats.invalid_lookups:,}\n\n"
        f"🌍 <b>Top Queried Regions:</b>{top_countries_text}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔒 <i>Privacy enforced: Zero raw numbers stored.</i>"
    )


def format_rate_limit_message(retry_after: int) -> str:
    """Return rate limit exceeded notification."""
    return (
        "⏳ <b>Too many requests!</b>\n\n"
        f"Please wait <b>{retry_after} second{'s' if retry_after != 1 else ''}</b> before submitting another query.\n\n"
        "<i>Rate limits protect bot availability for all users.</i>"
    )
