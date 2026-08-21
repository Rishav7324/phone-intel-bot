"""Handlers for IP, Ping, HTTP Headers, and Port testing commands."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.services.formatter import escape
from bot.tools.ip_tool import check_headers, check_ping, check_port, lookup_ip

logger = logging.getLogger(__name__)


async def ip_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ip <ip_or_domain>."""
    if not update.effective_message:
        return

    if not context.args:
        await update.effective_message.reply_text(
            "🌐 <b>IP & Network Intelligence</b>\n\n"
            "Query geolocation, ISP, ASN, and VPN/Proxy risk.\n\n"
            "<b>Usage:</b> <code>/ip &lt;IP address or domain&gt;</code>\n\n"
            "<b>Examples:</b>\n"
            "• <code>/ip 8.8.8.8</code>\n"
            "• <code>/ip 1.1.1.1</code>\n"
            "• <code>/ip github.com</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    target = context.args[0].strip()
    status_msg = await update.effective_message.reply_text("🔎 <i>Querying IP intelligence...</i>", parse_mode=ParseMode.HTML)

    res = await lookup_ip(target)
    if not res.get("success"):
        await status_msg.edit_text(f"❌ <b>Error:</b> {escape(res.get('error'))}", parse_mode=ParseMode.HTML)
        return

    text = (
        f"🌐 <b>IP INTELLIGENCE REPORT</b> {res.get('flag')}\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔢 <b>Target IP:</b> <code>{escape(res.get('ip'))}</code>\n"
        f"🌍 <b>Country:</b> {res.get('flag')} {escape(res.get('country'))} (<code>{escape(res.get('country_code'))}</code>)\n"
        f"📍 <b>Location:</b> {escape(res.get('city'))}, {escape(res.get('region'))} ({escape(res.get('zip'))})\n"
        f"🕐 <b>Timezone:</b> {escape(res.get('timezone'))}\n"
        f"🏢 <b>ISP:</b> {escape(res.get('isp'))}\n"
        f"🏢 <b>Organization:</b> {escape(res.get('org'))}\n"
        f"📡 <b>ASN:</b> <code>{escape(res.get('asn'))}</code>\n"
        f"🔄 <b>Reverse DNS:</b> <code>{escape(res.get('reverse_dns'))}</code>\n"
        f"🛡️ <b>Type / Risk:</b> {escape(res.get('risk_tag'))}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "ℹ️ <i>Public BGP and IP allocation data</i>"
    )
    await status_msg.edit_text(text, parse_mode=ParseMode.HTML)


async def ping_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /ping <host>."""
    if not update.effective_message:
        return

    if not context.args:
        await update.effective_message.reply_text("⏱️ <b>Usage:</b> <code>/ping &lt;domain or IP&gt;</code>\nExample: <code>/ping google.com</code>", parse_mode=ParseMode.HTML)
        return

    host = context.args[0].strip()
    status_msg = await update.effective_message.reply_text(f"⏱️ <i>Measuring latency to {escape(host)}...</i>", parse_mode=ParseMode.HTML)

    res = await check_ping(host)
    if not res.get("success"):
        await status_msg.edit_text(f"❌ <b>Ping Failed:</b> {escape(res.get('error'))}", parse_mode=ParseMode.HTML)
        return

    text = (
        "⏱️ <b>LATENCY / PING REPORT</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🌐 <b>Host:</b> <code>{escape(res.get('host'))}</code>\n"
        f"🔢 <b>IP:</b> <code>{escape(res.get('ip'))}</code>\n"
        f"🚪 <b>Port:</b> <code>{res.get('port')}</code>\n\n"
        f"⚡ <b>DNS Resolution:</b> <code>{res.get('dns_ms')} ms</code>\n"
        f"⚡ <b>TCP Handshake:</b> <code>{res.get('tcp_ms')} ms</code>\n"
        f"🚀 <b>Total Response Time:</b> <b>{res.get('total_ms')} ms</b>\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await status_msg.edit_text(text, parse_mode=ParseMode.HTML)


async def headers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /headers <url>."""
    if not update.effective_message:
        return

    if not context.args:
        await update.effective_message.reply_text("📡 <b>Usage:</b> <code>/headers &lt;website url&gt;</code>\nExample: <code>/headers github.com</code>", parse_mode=ParseMode.HTML)
        return

    url = context.args[0].strip()
    status_msg = await update.effective_message.reply_text("📡 <i>Fetching HTTP response headers...</i>", parse_mode=ParseMode.HTML)

    res = await check_headers(url)
    if not res.get("success"):
        await status_msg.edit_text(f"❌ <b>Error:</b> {escape(res.get('error'))}", parse_mode=ParseMode.HTML)
        return

    headers_lines = []
    for k, v in list(res.get("headers", {}).items())[:12]:
        headers_lines.append(f"• <b>{escape(k)}:</b> <code>{escape(v[:80])}</code>")

    text = (
        "📡 <b>HTTP RESPONSE HEADERS</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🌐 <b>Target:</b> <code>{escape(res.get('url'))}</code>\n"
        f"📊 <b>Status:</b> <code>{res.get('status_code')}</code>\n"
        f"🖥️ <b>Server:</b> <code>{escape(res.get('server'))}</code>\n\n"
        "<b>Headers Preview:</b>\n"
        + "\n".join(headers_lines) +
        "\n\n━━━━━━━━━━━━━━━━━━"
    )
    await status_msg.edit_text(text, parse_mode=ParseMode.HTML)


async def port_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /port <host> <port>."""
    if not update.effective_message:
        return

    if not context.args or len(context.args) < 2 or not context.args[1].isdigit():
        await update.effective_message.reply_text(
            "🚪 <b>Port Accessibility Checker</b>\n\n"
            "<b>Usage:</b> <code>/port &lt;host&gt; &lt;port_number&gt;</code>\n\n"
            "<b>Examples:</b>\n"
            "• <code>/port github.com 443</code>\n"
            "• <code>/port google.com 80</code>\n"
            "• <code>/port 1.1.1.1 53</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    host = context.args[0].strip()
    port = int(context.args[1].strip())

    status_msg = await update.effective_message.reply_text(f"🚪 <i>Checking port {port} on {escape(host)}...</i>", parse_mode=ParseMode.HTML)
    res = await check_port(host, port)

    is_open = res.get("is_open", False)
    status_str = "🟢 <b>OPEN / ACCESSIBLE</b>" if is_open else "🔴 <b>CLOSED / FILTERED</b>"

    text = (
        "🚪 <b>PORT STATUS REPORT</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🌐 <b>Host:</b> <code>{escape(host)}</code>\n"
        f"🔢 <b>Port:</b> <code>{port}</code>\n"
        f"📊 <b>Status:</b> {status_str}\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await status_msg.edit_text(text, parse_mode=ParseMode.HTML)
