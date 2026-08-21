"""Handler for /broadcast admin command to broadcast announcements to users."""

import asyncio
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from bot.config import get_settings
from bot.database.db import DatabaseManager

logger = logging.getLogger(__name__)


async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /broadcast <message> command (Admin Only)."""
    if not update.effective_message or not update.effective_user:
        return

    settings = get_settings()
    user_id = update.effective_user.id

    if not settings.is_admin(user_id):
        await update.effective_message.reply_text(
            "⛔ <b>Access Denied:</b> This command is restricted to bot administrators.",
            parse_mode=ParseMode.HTML,
        )
        return

    if not context.args:
        await update.effective_message.reply_text(
            "📢 <b>Admin Broadcast Tool</b>\n\n"
            "Usage: <code>/broadcast &lt;your message here&gt;</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    message_text = " ".join(context.args)
    db: DatabaseManager = context.bot_data.get("db")
    if not db:
        await update.effective_message.reply_text("⚠️ Database is not accessible.")
        return

    user_ids = await db.get_all_user_ids()
    if not user_ids:
        await update.effective_message.reply_text("⚠️ No registered users found in database.")
        return

    status_msg = await update.effective_message.reply_text(
        f"⏳ Broadcasting message to {len(user_ids)} users...",
        parse_mode=ParseMode.HTML,
    )

    success_count = 0
    fail_count = 0

    broadcast_content = (
        "📢 <b>BOT ANNOUNCEMENT</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{message_text}\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    for target_uid in user_ids:
        try:
            await context.bot.send_message(
                chat_id=target_uid,
                text=broadcast_content,
                parse_mode=ParseMode.HTML,
            )
            success_count += 1
            await asyncio.sleep(0.05)  # Telegram broadcast throttling
        except TelegramError:
            fail_count += 1

    await status_msg.edit_text(
        f"✅ <b>Broadcast Completed!</b>\n\n"
        f"• Sent successfully: <b>{success_count}</b>\n"
        f"• Failed / Blocked: <b>{fail_count}</b>",
        parse_mode=ParseMode.HTML,
    )
