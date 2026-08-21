"""Handler for the /start command."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.database.db import DatabaseManager
from bot.handlers.menu_handler import build_main_menu_keyboard
from bot.services.formatter import format_start_message

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command by providing a welcome message and interactive multi-tool dashboard."""
    if not update.effective_message or not update.effective_user:
        return

    user_id = update.effective_user.id
    db: DatabaseManager = context.bot_data.get("db")
    user_lang = await db.get_user_language(user_id) if db else "en"

    reply_markup = build_main_menu_keyboard()

    await update.effective_message.reply_text(
        text=format_start_message(lang=user_lang),
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )
    logger.info("User %s triggered /start (lang=%s)", user_id, user_lang)
