"""Handler for the /privacy command."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.services.formatter import format_privacy_message

logger = logging.getLogger(__name__)


async def privacy_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /privacy command explaining data handling and zero-log policy."""
    if not update.effective_message:
        return

    await update.effective_message.reply_text(
        text=format_privacy_message(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
