"""Handler for /email command verifying deliverability, MX servers, and disposable burner mail."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.services.formatter import escape
from bot.tools.email_tool import validate_email

logger = logging.getLogger(__name__)


async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /email <address>."""
    if not update.effective_message:
        return

    if not context.args:
        await update.effective_message.reply_text(
            "📧 <b>Email Validator & Spam Checker</b>\n\n"
            "Verify email syntax, MX mail exchange servers, and disposable burner addresses.\n\n"
            "<b>Usage:</b> <code>/email &lt;email address&gt;</code>\n\n"
            "<b>Examples:</b>\n"
            "• <code>/email user@gmail.com</code>\n"
            "• <code>/email test@temp-mail.org</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    raw_email = context.args[0].strip()
    status_msg = await update.effective_message.reply_text("🔎 <i>Checking email syntax and MX records...</i>", parse_mode=ParseMode.HTML)

    res = await validate_email(raw_email)

    mx_preview = "\n".join(f"• <code>{escape(m)}</code>" for m in res.get("mx_records", [])[:4])

    text = (
        "📧 <b>EMAIL VALIDATION REPORT</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"✉️ <b>Email:</b> <code>{escape(res.get('email'))}</code>\n"
        f"👤 <b>Username:</b> <code>{escape(res.get('user'))}</code>\n"
        f"🌐 <b>Domain:</b> <code>{escape(res.get('domain'))}</code>\n\n"
        f"📊 <b>Status:</b> {res.get('status')}\n"
        f"💡 <b>Diagnosis:</b> {escape(res.get('reason'))}\n\n"
        f"📬 <b>Mail Exchanger (MX) Records:</b>\n"
        + (mx_preview if mx_preview else "<i>No active mail servers found.</i>") +
        "\n\n━━━━━━━━━━━━━━━━━━"
    )
    await status_msg.edit_text(text, parse_mode=ParseMode.HTML)
