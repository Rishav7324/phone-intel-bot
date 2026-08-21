"""Handler for /dialcodes command displaying a global international dialling directory."""

import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from bot.utils.country_data import COUNTRY_DIRECTORY

logger = logging.getLogger(__name__)


async def dialcodes_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /dialcodes command showing a structured list of world dialling codes."""
    if not update.effective_message:
        return

    lines = [
        "🌐 <b>INTERNATIONAL DIALLING CODE DIRECTORY</b>",
        "━━━━━━━━━━━━━━━━━━\n",
        "<b>🌍 Asia & Middle East:</b>\n"
        "• 🇮🇳 India: <code>+91</code> | 🇵🇰 Pakistan: <code>+92</code>\n"
        "• 🇧🇩 Bangladesh: <code>+880</code> | 🇳🇵 Nepal: <code>+977</code>\n"
        "• 🇦🇪 UAE: <code>+971</code> | 🇸🇦 Saudi: <code>+966</code>\n"
        "• 🇸🇬 Singapore: <code>+65</code> | 🇯🇵 Japan: <code>+81</code>\n"
        "• 🇨🇳 China: <code>+86</code> | 🇲🇾 Malaysia: <code>+60</code>\n",
        "<b>🌎 Americas:</b>\n"
        "• 🇺🇸 USA: <code>+1</code> | 🇨🇦 Canada: <code>+1</code>\n"
        "• 🇧🇷 Brazil: <code>+55</code> | 🇲🇽 Mexico: <code>+52</code>\n",
        "<b>🌍 Europe:</b>\n"
        "• 🇬🇧 UK: <code>+44</code> | 🇩🇪 Germany: <code>+49</code>\n"
        "• 🇫🇷 France: <code>+33</code> | 🇮🇹 Italy: <code>+39</code>\n"
        "• 🇪🇸 Spain: <code>+34</code> | 🇷🇺 Russia: <code>+7</code>\n",
        "<b>🌍 Africa & Oceania:</b>\n"
        "• 🇳🇬 Nigeria: <code>+234</code> | 🇿🇦 South Africa: <code>+27</code>\n"
        "• 🇦🇺 Australia: <code>+61</code> | 🇳🇿 New Zealand: <code>+64</code>\n",
        "━━━━━━━━━━━━━━━━━━\n",
        "💡 <i>Tip: Use <code>/country &lt;name&gt;</code> for detailed profile on any country!</i>"
    ]

    await update.effective_message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)
