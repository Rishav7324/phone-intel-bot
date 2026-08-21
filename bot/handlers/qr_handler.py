"""Handlers for generating custom text, URL, and Wi-Fi QR Codes."""

import io
import logging
import qrcode
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.services.formatter import escape

logger = logging.getLogger(__name__)


async def qr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /qr <text_or_url>."""
    if not update.effective_message:
        return

    if not context.args:
        await update.effective_message.reply_text(
            "📲 <b>QR Code Generator</b>\n\n"
            "Generate high-resolution QR codes for any text, link, or crypto address.\n\n"
            "<b>Usage:</b> <code>/qr &lt;text or URL&gt;</code>\n\n"
            "<b>Example:</b>\n"
            "• <code>/qr https://github.com/Rishav7324/phone-intel-bot</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    payload = " ".join(context.args)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    bio.name = "qrcode.png"

    caption = f"📲 <b>Custom QR Code</b>\n\n<b>Payload:</b> <code>{escape(payload[:80])}</code>"
    await update.effective_message.reply_photo(photo=bio, caption=caption, parse_mode=ParseMode.HTML)


async def qrwifi_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /qrwifi <SSID> <Password> [WPA/WEP/nopass]."""
    if not update.effective_message:
        return

    if not context.args or len(context.args) < 2:
        await update.effective_message.reply_text(
            "📶 <b>Wi-Fi Connect QR Generator</b>\n\n"
            "Generate a Wi-Fi QR code so guests can scan and connect instantly!\n\n"
            "<b>Usage:</b> <code>/qrwifi &lt;SSID/NetworkName&gt; &lt;Password&gt; [SecurityType]</code>\n\n"
            "<b>Example:</b>\n"
            "• <code>/qrwifi Home_Fiber MySecurePass123 WPA</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    ssid = context.args[0]
    password = context.args[1]
    sec_type = context.args[2].upper() if len(context.args) >= 3 else "WPA"

    wifi_payload = f"WIFI:S:{ssid};T:{sec_type};P:{password};;"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(wifi_payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1E3A8A", back_color="#FFFFFF")
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    bio.name = "wifi_qr.png"

    caption = (
        "📶 <b>Wi-Fi Quick Connect QR Code</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🌐 <b>Network (SSID):</b> <code>{escape(ssid)}</code>\n"
        f"🔒 <b>Security:</b> {escape(sec_type)}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📲 <i>Point your phone camera at this QR code to join Wi-Fi automatically.</i>"
    )
    await update.effective_message.reply_photo(photo=bio, caption=caption, parse_mode=ParseMode.HTML)
