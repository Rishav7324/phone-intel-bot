"""Handlers for DNS resolution, URL unshortener, subdomains, and security scans."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.services.formatter import escape
from bot.tools.domain_tool import find_subdomains, lookup_dns, security_scan, unshorten_url

logger = logging.getLogger(__name__)


async def dns_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /dns <domain>."""
    if not update.effective_message:
        return

    if not context.args:
        await update.effective_message.reply_text("🔗 <b>Usage:</b> <code>/dns &lt;domain&gt;</code>\nExample: <code>/dns cloudflare.com</code>", parse_mode=ParseMode.HTML)
        return

    domain = context.args[0].strip()
    status_msg = await update.effective_message.reply_text(f"🔎 <i>Querying DNS records for {escape(domain)}...</i>", parse_mode=ParseMode.HTML)

    res = await lookup_dns(domain)
    if not res.get("success"):
        await status_msg.edit_text(f"❌ <b>DNS Lookup Failed:</b> {escape(res.get('error'))}", parse_mode=ParseMode.HTML)
        return

    lines = [
        f"🔗 <b>DNS RECORDS FOR {escape(res.get('domain').upper())}</b>",
        "━━━━━━━━━━━━━━━━━━\n",
    ]

    records = res.get("records", {})
    for r_type, entries in records.items():
        if entries:
            lines.append(f"📌 <b>{r_type} Records:</b>")
            for entry in entries[:5]:
                lines.append(f"  • <code>{escape(entry)}</code>")
            lines.append("")

    if res.get("total_records", 0) == 0:
        lines.append("<i>No public DNS records resolved.</i>\n")

    lines.extend([
        "━━━━━━━━━━━━━━━━━━",
        f"📊 <b>Total Records:</b> {res.get('total_records')}"
    ])

    await status_msg.edit_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def unshorten_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /unshorten <short_url>."""
    if not update.effective_message:
        return

    if not context.args:
        await update.effective_message.reply_text(
            "🛡️ <b>URL Unshortener & Anti-Phishing</b>\n\n"
            "Reveal the true destination of shortened links.\n\n"
            "<b>Usage:</b> <code>/unshorten &lt;shortened URL&gt;</code>\n\n"
            "<b>Examples:</b>\n"
            "• <code>/unshorten bit.ly/3xX...</code>\n"
            "• <code>/unshorten t.co/...</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    short_url = context.args[0].strip()
    status_msg = await update.effective_message.reply_text("🔎 <i>Tracing redirect chain...</i>", parse_mode=ParseMode.HTML)

    res = await unshorten_url(short_url)
    if not res.get("success"):
        await status_msg.edit_text(f"❌ <b>Error:</b> {escape(res.get('error'))}", parse_mode=ParseMode.HTML)
        return

    hops_text = ""
    for idx, hop in enumerate(res.get("hops", []), start=1):
        hops_text += f"\n  <b>Hop {idx}</b> ({hop.get('status_code')}): <code>{escape(hop.get('url'))}</code>"

    text = (
        "🛡️ <b>URL EXPANSION REPORT</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔗 <b>Initial Link:</b> <code>{escape(res.get('initial_url'))}</code>\n"
        f"🎯 <b>Final Target:</b> <code>{escape(res.get('final_url'))}</code>\n"
        f"🔀 <b>Redirect Hops:</b> {res.get('hops_count')}\n\n"
        f"<b>Redirect Path:</b>{hops_text}\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await status_msg.edit_text(text, parse_mode=ParseMode.HTML)


async def subdomains_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /subdomains <domain>."""
    if not update.effective_message:
        return

    if not context.args:
        await update.effective_message.reply_text("🌐 <b>Usage:</b> <code>/subdomains &lt;domain&gt;</code>\nExample: <code>/subdomains telegram.org</code>", parse_mode=ParseMode.HTML)
        return

    domain = context.args[0].strip()
    status_msg = await update.effective_message.reply_text(f"🔎 <i>Querying Certificate Transparency logs for {escape(domain)}...</i>", parse_mode=ParseMode.HTML)

    res = await find_subdomains(domain)
    if not res.get("success"):
        await status_msg.edit_text(f"❌ <b>Error:</b> {escape(res.get('error'))}", parse_mode=ParseMode.HTML)
        return

    sub_list = res.get("subdomains", [])
    preview_subs = "\n".join(f"• <code>{escape(s)}</code>" for s in sub_list[:25])

    text = (
        f"🌐 <b>SUBDOMAINS FOR {escape(res.get('domain').upper())}</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>Discovered Subdomains ({res.get('count')}):</b>\n"
        + (preview_subs if preview_subs else "<i>No active subdomains found in CT logs.</i>") +
        "\n\n━━━━━━━━━━━━━━━━━━\n"
        "ℹ️ <i>Source: Public Certificate Transparency (crt.sh)</i>"
    )
    await status_msg.edit_text(text, parse_mode=ParseMode.HTML)


async def secscan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /secscan <domain>."""
    if not update.effective_message:
        return

    if not context.args:
        await update.effective_message.reply_text("🛡️ <b>Usage:</b> <code>/secscan &lt;domain&gt;</code>\nExample: <code>/secscan google.com</code>", parse_mode=ParseMode.HTML)
        return

    domain = context.args[0].strip()
    status_msg = await update.effective_message.reply_text(f"🛡️ <i>Auditing HTTP security headers for {escape(domain)}...</i>", parse_mode=ParseMode.HTML)

    res = await security_scan(domain)
    if not res.get("success"):
        await status_msg.edit_text(f"❌ <b>Scan Failed:</b> {escape(res.get('error'))}", parse_mode=ParseMode.HTML)
        return

    checks_lines = []
    for check_name, is_passed in res.get("checks", {}).items():
        icon = "✅" if is_passed else "❌"
        checks_lines.append(f"{icon} {escape(check_name)}")

    text = (
        f"🛡️ <b>SECURITY HEADERS AUDIT FOR {escape(res.get('domain').upper())}</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🏆 <b>Overall Grade:</b> {res.get('grade')}\n"
        f"📊 <b>Score:</b> <b>{res.get('score')}</b>\n"
        f"🖥️ <b>Server:</b> <code>{escape(res.get('server'))}</code>\n\n"
        "<b>Security Checks:</b>\n"
        + "\n".join(checks_lines) +
        "\n\n━━━━━━━━━━━━━━━━━━"
    )
    await status_msg.edit_text(text, parse_mode=ParseMode.HTML)
