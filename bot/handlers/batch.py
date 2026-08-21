"""Handler for /batch command guiding users on multi-number analysis."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def batch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /batch command explaining how to run batch queries."""
    if not update.effective_message:
        return

    await update.effective_message.reply_text(
        "📊 <b>Batch Multi-Number Lookup</b>\n\n"
        "You can analyze up to <b>10 phone numbers at once</b>!\n\n"
        "<b>How to use:</b>\n"
        "Simply send a message with numbers separated by newlines or commas.\n\n"
        "<b>Example:</b>\n"
        "<code>+91 98765 43210\n"
        "+1 202 555 0123\n"
        "+44 20 7946 0958</code>\n\n"
        "The bot will automatically process each number and generate a structured comparative report.",
        parse_mode=ParseMode.HTML,
    )
