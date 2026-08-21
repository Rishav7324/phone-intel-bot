"""Handler for /language command and bilingual localization."""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.database.db import DatabaseManager

logger = logging.getLogger(__name__)


async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /language command presenting language options."""
    if not update.effective_message:
        return

    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"),
            InlineKeyboardButton("🇮🇳 हिन्दी (Hindi)", callback_data="set_lang_hi"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        "🌐 <b>Select Your Preferred Language / भाषा चुनें:</b>",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
    )
