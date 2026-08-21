"""Handlers for live Crypto prices and Forex exchange calculator."""

import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.services.formatter import escape
from bot.tools.market_tool import convert_currency, get_crypto_prices

logger = logging.getLogger(__name__)


async def crypto_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /crypto [coins]."""
    if not update.effective_message:
        return

    coins = context.args if context.args else ["BTC", "ETH", "SOL", "TON", "DOGE"]
    status_msg = await update.effective_message.reply_text("🪙 <i>Fetching live cryptocurrency market rates...</i>", parse_mode=ParseMode.HTML)

    res = await get_crypto_prices(coins)
    if not res.get("success"):
        await status_msg.edit_text(f"❌ <b>Error:</b> {escape(res.get('error'))}", parse_mode=ParseMode.HTML)
        return

    items = []
    for item in res.get("data", []):
        items.append(
            f"{item['icon']} <b>{item['label']}</b>\n"
            f"  • USD: <code>{item['usd']}</code> | INR: <code>{item['inr']}</code>\n"
            f"  • 24h Trend: {item['change']}\n"
        )

    text = (
        "🪙 <b>LIVE CRYPTOCURRENCY PRICES</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        + "\n".join(items) +
        "━━━━━━━━━━━━━━━━━━\n"
        "📈 <i>Data feed powered by CoinGecko</i>"
    )
    await status_msg.edit_text(text, parse_mode=ParseMode.HTML)


async def forex_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /forex <amount> <from> to <to> or /forex 100 USD INR."""
    if not update.effective_message:
        return

    if not context.args or len(context.args) < 3:
        await update.effective_message.reply_text(
            "💱 <b>Forex Currency Converter</b>\n\n"
            "<b>Usage:</b> <code>/forex &lt;amount&gt; &lt;FROM&gt; &lt;TO&gt;</code>\n\n"
            "<b>Examples:</b>\n"
            "• <code>/forex 100 USD INR</code>\n"
            "• <code>/forex 50 EUR USD</code>\n"
            "• <code>/forex 1000 AED INR</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    try:
        amount = float(context.args[0])
    except ValueError:
        await update.effective_message.reply_text("❌ Please specify a valid numerical amount.", parse_mode=ParseMode.HTML)
        return

    from_c = context.args[1].upper()
    to_c = context.args[2].upper()
    if to_c == "TO" and len(context.args) >= 4:
        to_c = context.args[3].upper()

    status_msg = await update.effective_message.reply_text("💱 <i>Calculating real-time exchange rates...</i>", parse_mode=ParseMode.HTML)

    res = await convert_currency(amount, from_c, to_c)
    if not res.get("success"):
        await status_msg.edit_text(f"❌ <b>Error:</b> {escape(res.get('error'))}", parse_mode=ParseMode.HTML)
        return

    text = (
        "💱 <b>CURRENCY CONVERSION RESULT</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💵 <b>{res['formatted_result']}</b>\n\n"
        f"📊 <b>Exchange Rate:</b> <code>1 {from_c} = {res['rate']} {to_c}</code>\n"
        f"🕒 <b>Last Update:</b> {res['updated_at']}\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )
    await status_msg.edit_text(text, parse_mode=ParseMode.HTML)
