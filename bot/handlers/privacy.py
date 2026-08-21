"""Handler for the /privacy command."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.database.db import DatabaseManager
from bot.services.formatter import format_privacy_message

logger = logging.getLogger(__name__)


async def privacy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /privacy command stating privacy principles and non-retention policies."""
    if not update.effective_message or not update.effective_user:
        return

    user_id = update.effective_user.id
    db: DatabaseManager = context.bot_data.get("db")
    user_lang = await db.get_user_language(user_id) if db else "en"

    await update.effective_message.reply_text(
        text=format_privacy_message(lang=user_lang),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
