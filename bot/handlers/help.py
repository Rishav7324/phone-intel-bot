"""Handler for the /help command."""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.database.db import DatabaseManager
from bot.services.formatter import format_help_message

logger = logging.getLogger(__name__)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command by providing complete categorized usage instructions and tips."""
    if not update.effective_message or not update.effective_user:
        return

    user_id = update.effective_user.id
    db: DatabaseManager = context.bot_data.get("db")
    user_lang = await db.get_user_language(user_id) if db else "en"

    keyboard = [
        [
            InlineKeyboardButton("🎛️ Master Menu", callback_data="menu_phone"),
            InlineKeyboardButton("🌐 Language", callback_data="open_language"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        text=format_help_message(lang=user_lang),
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )
