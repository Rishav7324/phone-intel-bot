"""Interactive multi-tool menu and dashboard handler."""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def build_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the master interactive toolkit menu."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📱 Phone Intel", callback_data="menu_phone"),
                InlineKeyboardButton("🌐 IP & Network", callback_data="menu_ip"),
            ],
            [
                InlineKeyboardButton("🔗 Domain & DNS", callback_data="menu_domain"),
                InlineKeyboardButton("📧 Email Checker", callback_data="menu_email"),
            ],
            [
                InlineKeyboardButton("📲 QR Code Studio", callback_data="menu_qr"),
                InlineKeyboardButton("🔐 Crypto & Hashes", callback_data="menu_crypto"),
            ],
            [
                InlineKeyboardButton("🪙 Crypto & Forex", callback_data="menu_market"),
                InlineKeyboardButton("🛠️ Dev Utilities", callback_data="menu_dev"),
            ],
            [
                InlineKeyboardButton("🌐 Language", callback_data="open_language"),
                InlineKeyboardButton("📖 Full Guide", callback_data="show_help"),
            ],
        ]
    )


async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /menu or /tools command."""
    if not update.effective_message:
        return

    text = (
        "🎛️ <b>MULTI-TOOL MASTER TOOLKIT (v2.0)</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome to your all-in-one Telegram Intelligence & Utility Suite!\n\n"
        "Select a tool category below or run any command directly:\n\n"
        "• <b>Phone Intel:</b> Send any number directly\n"
        "• <b>IP Lookup:</b> <code>/ip &lt;address&gt;</code>\n"
        "• <b>Domain & DNS:</b> <code>/dns &lt;domain&gt;</code>\n"
        "• <b>Email Verify:</b> <code>/email &lt;address&gt;</code>\n"
        "• <b>URL Unshortener:</b> <code>/unshorten &lt;link&gt;</code>\n"
        "• <b>Crypto & Forex:</b> <code>/crypto</code>, <code>/forex</code>\n"
        "• <b>QR Studio:</b> <code>/qr</code>, <code>/qrwifi</code>\n"
        "• <b>Security:</b> <code>/password</code>, <code>/hash</code>, <code>/secscan</code>\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )

    await update.effective_message.reply_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=build_main_menu_keyboard(),
    )
