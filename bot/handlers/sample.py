"""Handler for /sample command generating valid test phone numbers by country."""

import logging
import phonenumbers
from phonenumbers import PhoneNumberType, PhoneNumberFormat
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.utils.country_data import search_country, get_flag_emoji

logger = logging.getLogger(__name__)


async def sample_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /sample <country> (e.g. /sample India, /sample US, /sample Germany)."""
    if not update.effective_message:
        return

    if not context.args:
        await update.effective_message.reply_text(
            "🧪 <b>Sample Test Number Generator</b>\n\n"
            "Generate valid ITU-T example test numbers for testing.\n\n"
            "<b>Usage:</b> <code>/sample &lt;country name or ISO code&gt;</code>\n\n"
            "<b>Examples:</b>\n"
            "• <code>/sample India</code>\n"
            "• <code>/sample US</code>\n"
            "• <code>/sample UK</code>\n"
            "• <code>/sample Japan</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    query = " ".join(context.args).strip()
    country_info = search_country(query)

    if not country_info:
        await update.effective_message.reply_text(
            f"❌ <b>Country Not Found:</b> Could not find country <code>{query}</code>.",
            parse_mode=ParseMode.HTML,
        )
        return

    iso2 = country_info.iso2
    flag = country_info.flag

    # Generate examples for Mobile, Fixed Line, and Toll Free
    mobile_example = phonenumbers.example_number_for_type(iso2, PhoneNumberType.MOBILE)
    fixed_example = phonenumbers.example_number_for_type(iso2, PhoneNumberType.FIXED_LINE)
    toll_example = phonenumbers.example_number_for_type(iso2, PhoneNumberType.TOLL_FREE)

    lines = [
        f"{flag} <b>Valid Example Numbers for {country_info.name_en}</b>",
        "━━━━━━━━━━━━━━━━━━\n",
    ]

    if mobile_example:
        m_intl = phonenumbers.format_number(mobile_example, PhoneNumberFormat.INTERNATIONAL)
        m_natl = phonenumbers.format_number(mobile_example, PhoneNumberFormat.NATIONAL)
        lines.append(f"📱 <b>Mobile Example:</b>\n• International: <code>{m_intl}</code>\n• National: <code>{m_natl}</code>\n")

    if fixed_example:
        f_intl = phonenumbers.format_number(fixed_example, PhoneNumberFormat.INTERNATIONAL)
        f_natl = phonenumbers.format_number(fixed_example, PhoneNumberFormat.NATIONAL)
        lines.append(f"☎️ <b>Landline Example:</b>\n• International: <code>{f_intl}</code>\n• National: <code>{f_natl}</code>\n")

    if toll_example:
        t_intl = phonenumbers.format_number(toll_example, PhoneNumberFormat.INTERNATIONAL)
        lines.append(f"🏢 <b>Toll-Free Example:</b>\n• <code>{t_intl}</code>\n")

    lines.extend([
        "━━━━━━━━━━━━━━━━━━",
        "💡 <i>These are officially documented test numbers from ITU-T / libphonenumber databases.</i>"
    ])

    await update.effective_message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)
