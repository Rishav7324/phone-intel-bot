"""Handlers for phone number lookups, batch processing, QR codes, vCards, and interactive callbacks."""

import io
import json
import logging
import re
from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from bot.config import get_settings
from bot.database.db import DatabaseManager
from bot.services.formatter import (
    format_batch_report,
    format_help_message,
    format_lookup_report,
    format_privacy_message,
    format_rate_limit_message,
)
from bot.services.phone_lookup import PhoneLookupService
from bot.services.providers.base import NumberStatus, PhoneMetadata
from bot.utils.qr_generator import generate_contact_qr, generate_vcard
from bot.utils.rate_limit import RateLimiter

logger = logging.getLogger(__name__)


def build_report_keyboard(metadata: PhoneMetadata) -> InlineKeyboardMarkup:
    """Build interactive action buttons for single lookup reports."""
    buttons: List[List[InlineKeyboardButton]] = []
    num_identifier = metadata.e164_format or metadata.input_number

    # Row 1: Direct Action Links (WhatsApp / Telegram)
    action_row: List[InlineKeyboardButton] = []
    if metadata.wa_link and metadata.status in (NumberStatus.VALID, NumberStatus.POSSIBLE):
        action_row.append(InlineKeyboardButton("💬 WhatsApp", url=metadata.wa_link))
    if metadata.tg_link and metadata.status in (NumberStatus.VALID, NumberStatus.POSSIBLE):
        action_row.append(InlineKeyboardButton("✈️ Telegram", url=metadata.tg_link))
    if action_row:
        buttons.append(action_row)

    # Row 2: QR Code & vCard Contact Export
    if metadata.status in (NumberStatus.VALID, NumberStatus.POSSIBLE):
        buttons.append(
            [
                InlineKeyboardButton("📲 QR Code", callback_data=f"get_qr:{num_identifier}"),
                InlineKeyboardButton("📇 Save Contact (.vcf)", callback_data=f"get_vcf:{num_identifier}"),
            ]
        )

    # Row 3: Export JSON & Check Another
    buttons.append(
        [
            InlineKeyboardButton("📄 Export JSON", callback_data=f"export_json:{num_identifier}"),
            InlineKeyboardButton("🔄 Check Another", callback_data="check_another"),
        ]
    )

    # Row 4: Help & Language
    buttons.append(
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="show_help"),
            InlineKeyboardButton("🌐 Language", callback_data="open_language"),
        ]
    )
    return InlineKeyboardMarkup(buttons)


async def text_lookup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text queries (single number or batch of numbers)."""
    if not update.effective_message or not update.effective_message.text or not update.effective_user:
        return

    raw_text = update.effective_message.text.strip()
    user_id = update.effective_user.id
    settings = get_settings()

    db: DatabaseManager = context.bot_data.get("db")
    user_lang = await db.get_user_language(user_id) if db else "en"

    # Rate limiting check
    rate_limiter: RateLimiter = context.bot_data.get("rate_limiter")
    if rate_limiter:
        is_allowed, retry_after = await rate_limiter.is_allowed(user_id)
        if not is_allowed:
            logger.warning("Rate limit exceeded for user %s", user_id)
            await update.effective_message.reply_text(
                text=format_rate_limit_message(retry_after, lang=user_lang),
                parse_mode=ParseMode.HTML,
            )
            return

    potential_numbers = [n.strip() for n in re.split(r"[\n,]+", raw_text) if n.strip()]
    service: PhoneLookupService = context.bot_data.get("lookup_service")
    if not service:
        service = PhoneLookupService()

    # Case A: Batch query (2 to 10 numbers)
    if len(potential_numbers) > 1:
        if len(potential_numbers) > 10:
            potential_numbers = potential_numbers[:10]

        temp_msg = await update.effective_message.reply_text(
            f"🔎 <i>Analyzing batch of {len(potential_numbers)} numbers...</i>",
            parse_mode=ParseMode.HTML,
        )

        batch_results: List[PhoneMetadata] = []
        for num in potential_numbers:
            meta = await service.lookup(num, default_region=settings.default_region)
            batch_results.append(meta)
            if db:
                await db.record_lookup(
                    user_id=user_id,
                    country_code=meta.region_code or "UNKNOWN",
                    country_calling_code=meta.country_calling_code_str,
                    number_type=meta.number_type,
                    is_valid=meta.is_valid,
                )

        report_text = format_batch_report(batch_results, lang=user_lang)
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔄 Check Another", callback_data="check_another")]]
        )

        try:
            await temp_msg.edit_text(report_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        except TelegramError:
            await update.effective_message.reply_text(report_text, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        return

    # Case B: Single number query
    temp_msg = await update.effective_message.reply_text(
        "🔎 <i>Checking phone number metadata...</i>",
        parse_mode=ParseMode.HTML,
    )

    try:
        metadata = await service.lookup(
            raw_phone_number=raw_text,
            default_region=settings.default_region,
        )

        if db:
            await db.record_lookup(
                user_id=user_id,
                country_code=metadata.region_code or "UNKNOWN",
                country_calling_code=metadata.country_calling_code_str,
                number_type=metadata.number_type,
                is_valid=metadata.is_valid,
            )

        report_text = format_lookup_report(metadata, lang=user_lang)
        reply_markup = build_report_keyboard(metadata)

        try:
            await temp_msg.edit_text(
                text=report_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )
        except TelegramError:
            await update.effective_message.reply_text(
                text=report_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )

        logger.info(
            "Lookup completed for user %s: status=%s, country=%s",
            user_id,
            metadata.status.value,
            metadata.region_code or "Unknown",
        )

    except Exception as e:
        logger.error("Unexpected error during lookup execution: %s", e, exc_info=True)
        error_msg = (
            "⚠️ <b>An error occurred while processing your request.</b>\n\n"
            "Please ensure the number is formatted correctly (e.g. <code>+91 98765 43210</code>) "
            "and try again."
        )
        try:
            await temp_msg.edit_text(error_msg, parse_mode=ParseMode.HTML)
        except Exception:
            await update.effective_message.reply_text(error_msg, parse_mode=ParseMode.HTML)


async def callback_router_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route callback queries from inline buttons."""
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()

    data = query.data or ""
    user_id = update.effective_user.id
    db: DatabaseManager = context.bot_data.get("db")
    service: PhoneLookupService = context.bot_data.get("lookup_service") or PhoneLookupService()
    settings = get_settings()

    if data in ("check_number", "check_another"):
        await query.message.reply_text(
            "📱 <b>Send a phone number to check:</b>\n\n"
            "Please include the '+' prefix and country calling code.\n"
            "• <i>India:</i> <code>+91 98765 43210</code>\n"
            "• <i>US:</i> <code>+1 202 555 0123</code>\n"
            "• <i>UK:</i> <code>+44 20 7946 0958</code>\n\n"
            "💡 <i>Or send multiple numbers separated by newlines for batch analysis!</i>",
            parse_mode=ParseMode.HTML,
        )
    elif data == "show_help":
        keyboard = [[InlineKeyboardButton("🔍 Check Number", callback_data="check_number")]]
        await query.message.reply_text(
            text=format_help_message(),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True,
        )
    elif data == "show_privacy":
        await query.message.reply_text(
            text=format_privacy_message(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
    elif data == "open_language":
        keyboard = [
            [
                InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"),
                InlineKeyboardButton("🇮🇳 हिन्दी (Hindi)", callback_data="set_lang_hi"),
            ]
        ]
        await query.message.reply_text(
            "🌐 <b>Select Your Preferred Language / भाषा चुनें:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    elif data == "set_lang_en":
        if db:
            await db.set_user_language(user_id, "en")
        await query.message.reply_text("✅ Language set to <b>English</b>! Send any phone number to begin.", parse_mode=ParseMode.HTML)
    elif data == "set_lang_hi":
        if db:
            await db.set_user_language(user_id, "hi")
        await query.message.reply_text("✅ भाषा <b>हिन्दी</b> पर सेट हो गई है! विश्लेषण शुरू करने के लिए कोई भी फोन नंबर भेजें।", parse_mode=ParseMode.HTML)
    elif data.startswith("export_json:"):
        number_param = data.split(":", 1)[1]
        meta = await service.lookup(number_param, default_region=settings.default_region)
        json_data = json.dumps(meta.model_dump(), indent=2, ensure_ascii=False)

        bio = io.BytesIO(json_data.encode("utf-8"))
        bio.name = f"metadata_{re.sub(r'[^0-9]', '', meta.e164_format or 'lookup')}.json"

        await query.message.reply_document(
            document=bio,
            caption="📄 <b>Structured Phone Intelligence Metadata (JSON)</b>",
            parse_mode=ParseMode.HTML,
        )
    elif data.startswith("get_qr:"):
        number_param = data.split(":", 1)[1]
        qr_bio = generate_contact_qr(number_param)
        await query.message.reply_photo(
            photo=qr_bio,
            caption=f"📲 <b>Contact QR Code for</b> <code>{number_param}</code>\n<i>Scan with any camera to dial or save.</i>",
            parse_mode=ParseMode.HTML,
        )
    elif data.startswith("get_vcf:"):
        number_param = data.split(":", 1)[1]
        meta = await service.lookup(number_param, default_region=settings.default_region)
        vcf_bio = generate_vcard(meta)
        await query.message.reply_document(
            document=vcf_bio,
            caption=f"📇 <b>vCard Contact Card for</b> <code>{meta.international_format or number_param}</code>\n<i>Tap to import into Contacts.</i>",
            parse_mode=ParseMode.HTML,
        )
    elif data == "menu_phone":
        await query.message.reply_text(
            "📱 <b>Phone Intelligence Commands</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "• Send any phone number directly (e.g. <code>+91 98765 43210</code>)\n"
            "• <code>/country &lt;name&gt;</code> — Lookup country dialling codes & info\n"
            "• <code>/dialcodes</code> — Browse world dialling directory\n"
            "• <code>/sample &lt;country&gt;</code> — Generate test phone numbers\n"
            "• <code>/compare &lt;n1&gt; &lt;n2&gt;</code> — Side-by-side number comparison\n"
            "• <code>/batch</code> — Multi-number batch lookup guide",
            parse_mode=ParseMode.HTML,
        )
    elif data == "menu_ip":
        await query.message.reply_text(
            "🌐 <b>IP & Network Commands</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "• <code>/ip &lt;IP/domain&gt;</code> — Geolocation, ISP, ASN, and VPN check\n"
            "• <code>/ping &lt;host&gt;</code> — Measure TCP latency & DNS speed\n"
            "• <code>/headers &lt;url&gt;</code> — View HTTP response headers & server\n"
            "• <code>/port &lt;host&gt; &lt;port&gt;</code> — Test if a TCP port is open",
            parse_mode=ParseMode.HTML,
        )
    elif data == "menu_domain":
        await query.message.reply_text(
            "🔗 <b>Domain & Web OSINT Commands</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "• <code>/dns &lt;domain&gt;</code> — Query A, AAAA, MX, TXT, NS records\n"
            "• <code>/unshorten &lt;url&gt;</code> — Trace redirect chains & expand short links\n"
            "• <code>/subdomains &lt;domain&gt;</code> — Discover subdomains via CT logs\n"
            "• <code>/secscan &lt;domain&gt;</code> — Grade HTTP security headers",
            parse_mode=ParseMode.HTML,
        )
    elif data == "menu_email":
        await query.message.reply_text(
            "📧 <b>Email Verification Commands</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "• <code>/email &lt;address&gt;</code> — Validate syntax, MX mail exchange servers, and disposable/temp-mail status.",
            parse_mode=ParseMode.HTML,
        )
    elif data == "menu_qr":
        await query.message.reply_text(
            "📲 <b>QR Code Studio Commands</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "• <code>/qr &lt;text or url&gt;</code> — Generate custom QR code image\n"
            "• <code>/qrwifi &lt;SSID&gt; &lt;Pass&gt; [WPA]</code> — Generate Wi-Fi join QR code",
            parse_mode=ParseMode.HTML,
        )
    elif data == "menu_crypto":
        await query.message.reply_text(
            "🔐 <b>Cryptographic & Security Tools</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "• <code>/hash &lt;text&gt;</code> — Compute MD5, SHA-1, SHA-256, SHA-512\n"
            "• <code>/base64 enc &lt;text&gt;</code> — Base64 Encoder\n"
            "• <code>/base64 dec &lt;b64&gt;</code> — Base64 Decoder\n"
            "• <code>/password [len]</code> — Generate high-entropy secure password\n"
            "• <code>/uuid</code> — Generate UUID v4 / v1",
            parse_mode=ParseMode.HTML,
        )
    elif data == "menu_market":
        await query.message.reply_text(
            "🪙 <b>Crypto & Forex Trackers</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "• <code>/crypto [btc,eth,sol]</code> — Live crypto prices in USD & INR\n"
            "• <code>/forex &lt;amt&gt; &lt;from&gt; &lt;to&gt;</code> — Real-time currency exchange calculator",
            parse_mode=ParseMode.HTML,
        )
    elif data == "menu_dev":
        await query.message.reply_text(
            "🛠️ <b>Developer Utilities</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "• <code>/jwt &lt;token&gt;</code> — Decode JSON Web Token payload & header\n"
            "• <code>/epoch [ts]</code> — Convert Unix timestamp ↔ UTC / IST\n"
            "• <code>/color &lt;hex&gt;</code> — Convert HEX to RGB & generate color swatch\n"
            "• <code>/compare &lt;n1&gt; &lt;n2&gt;</code> — Side-by-side number comparison\n"
            "• <code>/sample &lt;country&gt;</code> — Generate valid test numbers",
            parse_mode=ParseMode.HTML,
        )

