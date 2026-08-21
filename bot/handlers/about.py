"""Handler for the /about command."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.services.formatter import format_about_message

logger = logging.getLogger(__name__)


async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command providing technical overview and features."""
    if not update.effective_message:
        return

    await update.effective_message.reply_text(
        text=format_about_message(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
