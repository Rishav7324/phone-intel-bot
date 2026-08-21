"""Handlers for cryptographic hashes, Base64, passwords, UUIDs, JWT tokens, Epoch, and Color swatches."""

import json
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.services.formatter import escape
from bot.tools.crypto_tool import (
    convert_color,
    convert_epoch,
    decode_jwt,
    generate_hashes,
    generate_password,
    generate_uuids,
    handle_base64,
)

logger = logging.getLogger(__name__)


async def hash_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /hash <text>."""
    if not update.effective_message:
        return

    if not context.args:
        await update.effective_message.reply_text("🔐 <b>Usage:</b> <code>/hash &lt;text to hash&gt;</code>\nExample: <code>/hash Hello World</code>", parse_mode=ParseMode.HTML)
        return

    text = " ".join(context.args)
    hashes = generate_hashes(text)

    res_text = (
        "🔐 <b>CRYPTOGRAPHIC HASH DIGESTS</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"📝 <b>Input:</b> <code>{escape(text[:50])}</code>\n\n"
        f"🔹 <b>MD5:</b>\n<code>{hashes['md5']}</code>\n\n"
        f"🔹 <b>SHA-1:</b>\n<code>{hashes['sha1']}</code>\n\n"
        f"🔹 <b>SHA-256:</b>\n<code>{hashes['sha256']}</code>\n\n"
        f"🔹 <b>SHA-512:</b>\n<code>{hashes['sha512']}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await update.effective_message.reply_text(res_text, parse_mode=ParseMode.HTML)


async def base64_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /base64 <enc|dec> <text>."""
    if not update.effective_message:
        return

    if not context.args or len(context.args) < 2:
        await update.effective_message.reply_text(
            "🔤 <b>Base64 Encoder / Decoder</b>\n\n"
            "<b>Usage:</b>\n"
            "• Encode: <code>/base64 enc &lt;text&gt;</code>\n"
            "• Decode: <code>/base64 dec &lt;base64_string&gt;</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    action = context.args[0]
    payload = " ".join(context.args[1:])

    success, result = handle_base64(action, payload)
    if not success:
        await update.effective_message.reply_text(f"❌ {result}", parse_mode=ParseMode.HTML)
        return

    label = "ENCODED RESULT" if action.lower() in ("enc", "encode") else "DECODED RESULT"
    await update.effective_message.reply_text(
        f"🔤 <b>BASE64 {label}</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"<code>{escape(result)}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━",
        parse_mode=ParseMode.HTML,
    )


async def password_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /password [length]."""
    if not update.effective_message:
        return

    length = 16
    if context.args and context.args[0].isdigit():
        length = int(context.args[0])

    pwd = generate_password(length=length, include_symbols=True)

    await update.effective_message.reply_text(
        "🔑 <b>SECURE RANDOM PASSWORD</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"<code>{escape(pwd)}</code>\n\n"
        f"📊 <b>Length:</b> {length} characters\n"
        "🛡️ <b>Entropy:</b> High (Uppercase, Lowercase, Digits, Symbols)\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Tap the password above to copy. Never shared or stored.</i>",
        parse_mode=ParseMode.HTML,
    )


async def uuid_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /uuid command."""
    if not update.effective_message:
        return

    uuids = generate_uuids()
    await update.effective_message.reply_text(
        "🆔 <b>GENERATED UNIQUE IDENTIFIERS</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔹 <b>UUID v4 (Random):</b>\n<code>{uuids['uuid4']}</code>\n\n"
        f"🔹 <b>UUID v1 (Timestamp):</b>\n<code>{uuids['uuid1']}</code>\n\n"
        f"🔹 <b>Hex (32 chars):</b>\n<code>{uuids['hex']}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━",
        parse_mode=ParseMode.HTML,
    )


async def jwt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /jwt <token>."""
    if not update.effective_message:
        return

    if not context.args:
        await update.effective_message.reply_text("🪙 <b>Usage:</b> <code>/jwt &lt;your.jwt.token&gt;</code>", parse_mode=ParseMode.HTML)
        return

    token = context.args[0].strip()
    res = decode_jwt(token)

    if not res.get("success"):
        await update.effective_message.reply_text(f"❌ <b>Error:</b> {escape(res.get('error'))}", parse_mode=ParseMode.HTML)
        return

    header_json = json.dumps(res.get("header"), indent=2)
    payload_json = json.dumps(res.get("payload"), indent=2)

    text = (
        "🪙 <b>JWT TOKEN DECODER</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"⚙️ <b>Algorithm:</b> <code>{escape(res.get('algorithm'))}</code>\n"
        f"📅 <b>Issued At (iat):</b> <code>{escape(res.get('issued_at'))}</code>\n"
        f"⏰ <b>Expires At (exp):</b> <code>{escape(res.get('expires_at'))}</code>\n\n"
        "<b>📦 Header:</b>\n"
        f"<pre><code class=\"language-json\">{escape(header_json)}</code></pre>\n"
        "<b>📦 Payload:</b>\n"
        f"<pre><code class=\"language-json\">{escape(payload_json)}</code></pre>\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)


async def epoch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /epoch [timestamp_or_date]."""
    if not update.effective_message:
        return

    arg = context.args[0] if context.args else None
    res = convert_epoch(arg)

    await update.effective_message.reply_text(
        "🕒 <b>UNIX EPOCH TIMESTAMP CONVERTER</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔢 <b>Epoch Timestamp:</b> <code>{res['epoch']}</code>\n"
        f"🌐 <b>UTC Time:</b> <code>{res['utc_str']}</code>\n"
        f"🇮🇳 <b>IST Time:</b> <code>{res['ist_str']}</code>\n"
        f"⏱️ <b>Relative:</b> {res['relative']}\n\n"
        "━━━━━━━━━━━━━━━━━━",
        parse_mode=ParseMode.HTML,
    )


async def color_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /color <hex_code>."""
    if not update.effective_message:
        return

    if not context.args:
        await update.effective_message.reply_text("🎨 <b>Usage:</b> <code>/color &lt;HEX code&gt;</code>\nExample: <code>/color #3B82F6</code> or <code>/color FF5733</code>", parse_mode=ParseMode.HTML)
        return

    hex_val = context.args[0].strip()
    color_info, img_bio = convert_color(hex_val)

    caption = (
        f"🎨 <b>COLOR PALETTE PREVIEW</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔹 <b>HEX:</b> <code>{color_info['hex']}</code>\n"
        f"🔹 <b>RGB:</b> <code>{color_info['rgb']}</code>\n"
        f"🔹 <b>Red:</b> {color_info['r']} | <b>Green:</b> {color_info['g']} | <b>Blue:</b> {color_info['b']}\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await update.effective_message.reply_photo(photo=img_bio, caption=caption, parse_mode=ParseMode.HTML)
