"""Handler for the /start command."""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.services.formatter import format_start_message

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command by providing a welcome message and interactive button."""
    if not update.effective_message:
        return

    keyboard = [
        [
            InlineKeyboardButton("🔍 Check Number", callback_data="check_number"),
            InlineKeyboardButton("📖 Help Guide", callback_data="show_help"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        text=format_start_message(),
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )
    user_id = update.effective_user.id if update.effective_user else "unknown"
    logger.info("User %s triggered /start", user_id)
