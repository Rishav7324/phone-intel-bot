"""Handlers for phone number lookups and interactive inline callbacks."""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import ContextTypes

from bot.config import get_settings
from bot.database.db import DatabaseManager
from bot.services.formatter import (
    format_help_message,
    format_lookup_report,
    format_privacy_message,
    format_rate_limit_message,
)
from bot.services.phone_lookup import PhoneLookupService
from bot.utils.rate_limit import RateLimiter

logger = logging.getLogger(__name__)


def get_report_keyboard() -> InlineKeyboardMarkup:
    """Return inline keyboard attached to lookup reports."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔄 Check Another", callback_data="check_another"),
                InlineKeyboardButton("ℹ️ Help", callback_data="show_help"),
            ]
        ]
    )


async def text_lookup_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages containing phone number queries."""
    if not update.effective_message or not update.effective_message.text or not update.effective_user:
        return

    raw_text = update.effective_message.text.strip()
    user_id = update.effective_user.id
    settings = get_settings()

    # Rate limiting check
    rate_limiter: RateLimiter = context.bot_data.get("rate_limiter")
    if rate_limiter:
        is_allowed, retry_after = await rate_limiter.is_allowed(user_id)
        if not is_allowed:
            logger.warning("Rate limit exceeded for user %s", user_id)
            await update.effective_message.reply_text(
                text=format_rate_limit_message(retry_after),
                parse_mode=ParseMode.HTML,
            )
            return

    # Send temporary searching indicator message
    temp_msg = await update.effective_message.reply_text(
        "🔎 <i>Checking phone number metadata...</i>",
        parse_mode=ParseMode.HTML,
    )

    try:
        # Retrieve lookup service
        service: PhoneLookupService = context.bot_data.get("lookup_service")
        if not service:
            service = PhoneLookupService()

        # Perform phone lookup
        metadata = await service.lookup(
            raw_phone_number=raw_text,
            default_region=settings.default_region,
        )

        # Record anonymous telemetry in database (non-blocking)
        db: DatabaseManager = context.bot_data.get("db")
        if db:
            await db.record_lookup(
                user_id=user_id,
                country_code=metadata.region_code or "UNKNOWN",
                country_calling_code=metadata.country_calling_code_str,
                number_type=metadata.number_type,
                is_valid=metadata.is_valid,
            )

        # Format final output report
        report_text = format_lookup_report(metadata)
        reply_markup = get_report_keyboard()

        # Update temporary message with final report
        try:
            await temp_msg.edit_text(
                text=report_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )
        except TelegramError:
            # If edit fails (e.g. timeout), send as new message
            await update.effective_message.reply_text(
                text=report_text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )

        logger.info(
            "Lookup completed for user %s: status=%s, country=%s",
            user_id,
            metadata.status.value,
            metadata.region_code or "Unknown",
        )

    except Exception as e:
        logger.error("Unexpected error during lookup execution: %s", e, exc_info=True)
        error_msg = (
            "⚠️ <b>An error occurred while processing your request.</b>\n\n"
            "Please ensure the number is formatted correctly (e.g. <code>+91 98765 43210</code>) "
            "and try again."
        )
        try:
            await temp_msg.edit_text(error_msg, parse_mode=ParseMode.HTML)
        except Exception:
            await update.effective_message.reply_text(error_msg, parse_mode=ParseMode.HTML)


async def callback_router_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route callback queries from inline buttons."""
    query = update.callback_query
    if not query:
        return

    await query.answer()

    data = query.data
    if data in ("check_number", "check_another"):
        await query.message.reply_text(
            "📱 <b>Send a phone number to check:</b>\n\n"
            "Please include the '+' prefix and country calling code.\n"
            "• <i>India:</i> <code>+91 98765 43210</code>\n"
            "• <i>US:</i> <code>+1 202 555 0123</code>\n"
            "• <i>UK:</i> <code>+44 20 7946 0958</code>",
            parse_mode=ParseMode.HTML,
        )
    elif data == "show_help":
        keyboard = [[InlineKeyboardButton("🔍 Check Number", callback_data="check_number")]]
        await query.message.reply_text(
            text=format_help_message(),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True,
        )
    elif data == "show_privacy":
        await query.message.reply_text(
            text=format_privacy_message(),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )
