"""Telegram HTML formatting helpers for reports, help screens, batch results, and administrative stats."""

import html
import json
from typing import List, Optional
from bot.database.db import AdminStats
from bot.services.providers.base import NumberStatus, PhoneMetadata
from bot.utils.country_data import CountryInfo


def escape(text: Optional[str]) -> str:
    """Safely escape HTML entities in user-controlled or metadata strings."""
    if text is None:
        return ""
    return html.escape(str(text))


def format_lookup_report(metadata: PhoneMetadata, lang: str = "en") -> str:
    """Format structured phone metadata into an enriched Telegram HTML report."""
    if metadata.status == NumberStatus.INVALID and metadata.error_message:
        if lang == "hi":
            return (
                "🔴 <b>फोन नंबर त्रुटि (Error)</b>\n"
                "━━━━━━━━━━━━━━━━━━\n\n"
                f"🔢 <b>इनपुट:</b> <code>{escape(metadata.input_number)}</code>\n\n"
                f"⚠️ <b>कारण:</b>\n{escape(metadata.error_message)}\n\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "💡 <i>सुझाव: हमेशा '+' और कंट्री कोड शामिल करें (उदा. <code>+91 98765 43210</code> या <code>+1 202 555 0123</code>).</i>"
            )
        return (
            "🔴 <b>PHONE LOOKUP ERROR</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🔢 <b>Input:</b> <code>{escape(metadata.input_number)}</code>\n\n"
            f"⚠️ <b>Reason:</b>\n{escape(metadata.error_message)}\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "💡 <i>Tip: Always include the '+' sign and country calling code (e.g. <code>+91 98765 43210</code> or <code>+1 202 555 0123</code>).</i>"
        )

    # Valid status icon and text
    if metadata.status == NumberStatus.VALID:
        valid_str = "✅ Yes (Valid ITU format)" if lang != "hi" else "✅ हाँ (वैध नंबर प्रारूप)"
    elif metadata.status == NumberStatus.POSSIBLE:
        valid_str = "🟡 Possible but unverified" if lang != "hi" else "🟡 संभव (अपुष्ट)"
    else:
        valid_str = "🔴 No (Invalid format)" if lang != "hi" else "🔴 नहीं (अवैध)"

    possible_str = ("✅ Yes" if metadata.is_possible else "🔴 No") if lang != "hi" else ("✅ हाँ" if metadata.is_possible else "🔴 नहीं")
    emergency_badge = " 🚨 <i>[Emergency Service Number]</i>" if metadata.is_emergency else ""
    display_num = metadata.international_format or metadata.e164_format or metadata.input_number
    calling_code = metadata.country_calling_code_str or (f"+{metadata.country_code}" if metadata.country_code else "Not available")
    timezones_str = ", ".join(metadata.timezones) if metadata.timezones else "Not available"

    flag = metadata.flag_emoji or "🌐"

    if lang == "hi":
        lines = [
            f"📱 <b>फोन नंबर इंटेलिजेंस रिपोर्ट</b> {flag}",
            "━━━━━━━━━━━━━━━━━━\n",
            f"🔢 <b>नंबर:</b> <code>{escape(display_num)}</code>{emergency_badge}\n",
            f"🌍 <b>देश:</b> {flag} {escape(metadata.country_name)}\n",
            f"📞 <b>कंट्री कोड:</b> <code>{escape(calling_code)}</code>\n",
            f"📱 <b>प्रकार:</b> {escape(metadata.number_type)}\n",
            f"🛡️ <b>सुरक्षा / रिस्क स्तर:</b> {escape(metadata.risk_level)} <i>({escape(metadata.risk_description)})</i>\n",
            f"✅ <b>वैध प्रारूप:</b> {valid_str}\n",
            f"🔎 <b>संभव:</b> {possible_str}\n",
            f"🏢 <b>ऑपरेटर (Carrier):</b> {escape(metadata.carrier)}\n",
            f"📍 <b>क्षेत्र (Region):</b> {escape(metadata.region_description)}\n",
            f"🕐 <b>समय क्षेत्र (Timezone):</b> {escape(timezones_str)}\n",
            f"🌐 <b>अंतर्राष्ट्रीय:</b> <code>{escape(metadata.international_format or 'Not available')}</code>\n",
            f"☎️ <b>राष्ट्रीय:</b> <code>{escape(metadata.national_format or 'Not available')}</code>\n",
        ]
        if metadata.capital:
            lines.append(f"🏛️ <b>राजधानी:</b> {escape(metadata.capital)} | 💰 <b>मुद्रा:</b> {escape(metadata.currency or 'N/A')}\n")
        lines.extend([
            "━━━━━━━━━━━━━━━━━━",
            "ℹ️ <i>केवल सार्वजनिक मेटाडेटा • स्वामित्व या लाइव स्थिति का प्रमाण नहीं</i>"
        ])
    else:
        lines = [
            f"📱 <b>PHONE LOOKUP REPORT</b> {flag}",
            "━━━━━━━━━━━━━━━━━━\n",
            f"🔢 <b>Number</b>\n<code>{escape(display_num)}</code>{emergency_badge}\n",
            f"🌍 <b>Country</b>\n{flag} {escape(metadata.country_name)}\n",
            f"📞 <b>Country Code</b>\n{escape(calling_code)}\n",
            f"📱 <b>Type</b>\n{escape(metadata.number_type)}\n",
            f"🛡️ <b>Risk Assessment</b>\n{escape(metadata.risk_level)} <i>({escape(metadata.risk_description)})</i>\n",
            f"✅ <b>Valid Format</b>\n{valid_str}\n",
            f"🔎 <b>Possible</b>\n{possible_str}\n",
            f"🏢 <b>Carrier</b>\n{escape(metadata.carrier)}\n",
            f"📍 <b>General Region</b>\n{escape(metadata.region_description)}\n",
            f"🕐 <b>Timezone</b>\n{escape(timezones_str)}\n",
            f"🌐 <b>International</b>\n<code>{escape(metadata.international_format or 'Not available')}</code>\n",
            f"☎️ <b>National</b>\n<code>{escape(metadata.national_format or 'Not available')}</code>\n",
        ]
        if metadata.capital:
            lines.append(f"🏛️ <b>Capital:</b> {escape(metadata.capital)} | 💰 <b>Currency:</b> {escape(metadata.currency or 'N/A')}\n")
        lines.extend([
            "━━━━━━━━━━━━━━━━━━",
            "ℹ️ <i>Public metadata only • Not proof of ownership or live status</i>"
        ])

    if metadata.used_default_region:
        lines.append("\n⚠️ <i>Parsed using default region setting.</i>" if lang != "hi" else "\n⚠️ <i>डिफ़ॉल्ट क्षेत्र सेटिंग का उपयोग करके पार्स किया गया।</i>")

    return "\n".join(lines)


def format_country_report(info: CountryInfo) -> str:
    """Format full country metadata profile."""
    return (
        f"{info.flag} <b>{escape(info.name_en)} ({escape(info.name_hi)})</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"📞 <b>Calling Code:</b> <code>{escape(info.calling_code)}</code>\n"
        f"🌐 <b>ISO Codes:</b> <code>{escape(info.iso2)}</code> / <code>{escape(info.iso3)}</code>\n"
        f"🏛️ <b>Capital:</b> {escape(info.capital)}\n"
        f"💰 <b>Currency:</b> {escape(info.currency)}\n"
        f"🗣️ <b>Languages:</b> {escape(info.languages)}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Tip: Send any phone number from this country to check detailed metadata!</i>"
    )


def format_batch_report(results: List[PhoneMetadata], lang: str = "en") -> str:
    """Format summary report for multiple phone lookups."""
    total = len(results)
    valid_count = sum(1 for r in results if r.is_valid)

    header = f"📊 <b>BATCH LOOKUP REPORT ({total} Numbers)</b>\n━━━━━━━━━━━━━━━━━━\n\n" if lang != "hi" else f"📊 <b>बैच विश्लेषण रिपोर्ट ({total} नंबर)</b>\n━━━━━━━━━━━━━━━━━━\n\n"
    items = []

    for idx, r in enumerate(results, start=1):
        status_icon = "✅" if r.is_valid else ("🟡" if r.is_possible else "🔴")
        num_str = r.international_format or r.e164_format or r.input_number
        country_str = f"{r.flag_emoji} {r.country_name}" if r.country_name != "Not available" else "Unknown"
        items.append(
            f"{idx}. {status_icon} <code>{escape(num_str)}</code>\n"
            f"    └ {country_str} • {escape(r.number_type)} • {escape(r.risk_level)}"
        )

    summary = (
        f"\n\n━━━━━━━━━━━━━━━━━━\n"
        f"📈 <b>Summary:</b> {valid_count}/{total} Valid Formats"
    )
    return header + "\n".join(items) + summary


def format_start_message(lang: str = "en") -> str:
    """Return welcome message for /start command."""
    if lang == "hi":
        return (
            "📱 <b>फोन इंटेलिजेंस बॉट (Phone Intelligence Bot)</b>\n\n"
            "मुझे कोई भी फोन नंबर भेजें और मैं उसका उपलब्ध सार्वजनिक मेटाडेटा निकालूँगा।\n\n"
            "<b>उदाहरण:</b>\n"
            "• <code>+91 98765 43210</code>\n"
            "• <code>+1 202 555 0123</code>\n"
            "• <code>+44 20 7946 0958</code>\n\n"
            "<b>विशेषताएँ:</b>\n"
            "• ITU-T प्रारूप वैधता और स्थिति\n"
            "• देश, ऑपरेटर और टेलीकॉम प्रकार\n"
            "• रिस्क व सुरक्षा स्तर\n"
            "• समय क्षेत्र (Timezone)\n"
            "• सीधा WhatsApp / Telegram चैट लिंक\n"
            "• /country — देश कोड निर्देशिका\n"
            "• /batch — एक साथ कई नंबर जांचें\n\n"
            "🔒 <b>गोपनीयता:</b> हम कभी कोई फोन नंबर स्टोर नहीं करते।\n\n"
            "शुरू करने के लिए नीचे <b>🔍 Check Number</b> पर क्लिक करें!"
        )

    return (
        "📱 <b>Phone Intelligence Bot</b>\n\n"
        "Send me any phone number and I'll analyze its available public metadata.\n\n"
        "<b>Examples:</b>\n"
        "• <code>+91 98765 43210</code>\n"
        "• <code>+1 202 555 0123</code>\n"
        "• <code>+44 20 7946 0958</code>\n\n"
        "<b>Upgraded Features:</b>\n"
        "• ITU-T format validity & carrier allocation\n"
        "• Telecom classification & risk assessment\n"
        "• Direct WhatsApp / Telegram chat generator\n"
        "• /country &lt;name&gt; — Country dialling directory\n"
        "• /batch — Analyze multiple numbers in one go\n"
        "• /export — Export metadata as JSON\n"
        "• /language — Switch English / Hindi\n\n"
        "🔒 <b>Privacy Notice:</b>\n"
        "Zero raw phone numbers are permanently stored.\n\n"
        "Click <b>🔍 Check Number</b> below to begin!"
    )


def format_help_message(lang: str = "en") -> str:
    """Return documentation message for /help command."""
    return (
        "📖 <b>Phone Intelligence Bot — Commands & Guide</b>\n\n"
        "<b>Available Commands:</b>\n"
        "• /start — Welcome screen & overview\n"
        "• /help — This usage guide\n"
        "• /country &lt;name/code&gt; — Lookup country calling codes & info\n"
        "• /batch — How to run multi-number lookups\n"
        "• /language — Switch English / Hindi UI\n"
        "• /privacy — Zero-log privacy principles\n"
        "• /about — Tech stack and architecture\n\n"
        "<b>Batch Lookup Syntax:</b>\n"
        "Send multiple numbers separated by newlines or commas (max 10 numbers).\n\n"
        "<b>Important Metadata Disclaimers:</b>\n"
        "• <i>Valid</i> indicates proper ITU structure, not active subscriber status.\n"
        "• <i>Carrier</i> indicates original range allocation, not current SIM owner.\n"
        "• <i>Region</i> indicates prefix area, not live GPS."
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
        "ℹ️ <b>About Phone Intelligence Bot (Upgraded v1.1)</b>\n\n"
        "A fast, secure, and production-grade Telegram bot providing public telephone number metadata.\n\n"
        "<b>Key Upgrades:</b>\n"
        "• Telecom risk scoring heuristics\n"
        "• Country dial code search engine\n"
        "• Batch multi-number processing\n"
        "• Direct messaging links (WhatsApp / Telegram)\n"
        "• Bilingual English & Hindi support\n"
        "• Emergency shortcode detection\n\n"
        "<b>Tech Stack:</b>\n"
        "Python 3.12+, python-telegram-bot v21+, Google's libphonenumber, Pydantic v2, aiosqlite."
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


def format_rate_limit_message(retry_after: int, lang: str = "en") -> str:
    """Return rate limit exceeded notification."""
    if lang == "hi":
        return (
            "⏳ <b>बहुत अधिक अनुरोध (Too many requests)!</b>\n\n"
            f"कृपया दोबारा प्रयास करने से पहले <b>{retry_after} सेकंड</b> प्रतीक्षा करें।"
        )
    return (
        "⏳ <b>Too many requests!</b>\n\n"
        f"Please wait <b>{retry_after} second{'s' if retry_after != 1 else ''}</b> before submitting another query.\n\n"
        "<i>Rate limits protect bot availability for all users.</i>"
    )
