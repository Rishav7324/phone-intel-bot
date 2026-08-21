"""Handler for /country command allowing users to look up country codes, flags, and dialling info."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.services.formatter import format_country_report
from bot.utils.country_data import search_country

logger = logging.getLogger(__name__)


async def country_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /country command (e.g. /country India, /country +44, /country US)."""
    if not update.effective_message:
        return

    # Check for arguments
    if not context.args:
        await update.effective_message.reply_text(
            "🌍 <b>Country Calling Code Search</b>\n\n"
            "Please provide a country name, ISO code, or dialling code.\n\n"
            "<b>Examples:</b>\n"
            "• <code>/country India</code>\n"
            "• <code>/country +1</code>\n"
            "• <code>/country Japan</code>\n"
            "• <code>/country GB</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    query = " ".join(context.args).strip()
    country_info = search_country(query)

    if not country_info:
        await update.effective_message.reply_text(
            f"❌ <b>Country Not Found:</b> Could not find country data matching <code>{query}</code>.\n\n"
            "Please check the spelling or try an international dial code (e.g. <code>+91</code>, <code>+1</code>, <code>+44</code>).",
            parse_mode=ParseMode.HTML,
        )
        return

    text = format_country_report(country_info)
    await update.effective_message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
    )
