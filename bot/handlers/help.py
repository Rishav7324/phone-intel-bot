"""Handler for the /help command."""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.services.formatter import format_help_message

logger = logging.getLogger(__name__)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command by providing usage instructions and tips."""
    if not update.effective_message:
        return

    keyboard = [
        [
            InlineKeyboardButton("🔍 Check Number", callback_data="check_number"),
            InlineKeyboardButton("🔒 Privacy Policy", callback_data="show_privacy"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        text=format_help_message(),
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )
