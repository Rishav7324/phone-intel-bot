"""Admin handler for usage statistics reporting."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.config import get_settings
from bot.database.db import DatabaseManager
from bot.services.formatter import format_admin_stats

logger = logging.getLogger(__name__)


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command for authorized administrators."""
    if not update.effective_message or not update.effective_user:
        return

    settings = get_settings()
    user_id = update.effective_user.id

    if not settings.is_admin(user_id):
        logger.warning("Unauthorized access attempt to /stats by user %s", user_id)
        await update.effective_message.reply_text(
            "⛔ <b>Access Denied:</b> This command is restricted to bot administrators.",
            parse_mode=ParseMode.HTML,
        )
        return

    # Retrieve database instance from bot_data
    db: DatabaseManager = context.bot_data.get("db")
    if not db:
        await update.effective_message.reply_text("⚠️ Database connection is not available.")
        return

    try:
        stats = await db.get_admin_stats()
        text = format_admin_stats(stats)
        await update.effective_message.reply_text(
            text=text,
            parse_mode=ParseMode.HTML,
        )
        logger.info("Admin %s generated system stats report", user_id)
    except Exception as e:
        logger.error("Error generating admin statistics: %s", e)
        await update.effective_message.reply_text(
            "⚠️ An error occurred while retrieving statistics. Please check server logs.",
            parse_mode=ParseMode.HTML,
        )
