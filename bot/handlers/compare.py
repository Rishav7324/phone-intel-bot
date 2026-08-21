"""Handler for /compare command comparing two phone numbers side-by-side."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.config import get_settings
from bot.services.formatter import escape
from bot.services.phone_lookup import PhoneLookupService

logger = logging.getLogger(__name__)


async def compare_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /compare <num1> <num2> command."""
    if not update.effective_message:
        return

    if not context.args or len(context.args) < 2:
        await update.effective_message.reply_text(
            "⚖️ <b>Phone Number Comparison Tool</b>\n\n"
            "Compare two phone numbers side-by-side.\n\n"
            "<b>Usage:</b> <code>/compare &lt;number1&gt; &lt;number2&gt;</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/compare +919876543210 +12025550123</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    num1_raw, num2_raw = context.args[0], context.args[1]
    service: PhoneLookupService = context.bot_data.get("lookup_service")
    if not service:
        service = PhoneLookupService()
    settings = get_settings()

    meta1 = await service.lookup(num1_raw, default_region=settings.default_region)
    meta2 = await service.lookup(num2_raw, default_region=settings.default_region)

    n1_disp = meta1.international_format or meta1.input_number
    n2_disp = meta2.international_format or meta2.input_number

    v1 = "✅ Valid" if meta1.is_valid else "🔴 Invalid"
    v2 = "✅ Valid" if meta2.is_valid else "🔴 Invalid"

    report = (
        "⚖️ <b>SIDE-BY-SIDE NUMBER COMPARISON</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>1️⃣ Number 1:</b> <code>{escape(n1_disp)}</code>\n"
        f"• Country: {meta1.flag_emoji} {escape(meta1.country_name)} ({escape(meta1.country_calling_code_str or 'N/A')})\n"
        f"• Type: {escape(meta1.number_type)}\n"
        f"• Carrier: {escape(meta1.carrier)}\n"
        f"• Validity: {v1}\n"
        f"• Risk: {escape(meta1.risk_level)}\n"
        f"• Timezone: {escape(', '.join(meta1.timezones))}\n\n"
        f"<b>2️⃣ Number 2:</b> <code>{escape(n2_disp)}</code>\n"
        f"• Country: {meta2.flag_emoji} {escape(meta2.country_name)} ({escape(meta2.country_calling_code_str or 'N/A')})\n"
        f"• Type: {escape(meta2.number_type)}\n"
        f"• Carrier: {escape(meta2.carrier)}\n"
        f"• Validity: {v2}\n"
        f"• Risk: {escape(meta2.risk_level)}\n"
        f"• Timezone: {escape(', '.join(meta2.timezones))}\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    await update.effective_message.reply_text(report, parse_mode=ParseMode.HTML)
