"""Main entry point for Telegram Multi-Tool Intelligence & Utility Bot (v2.0)."""

import asyncio
import logging
import signal
import sys
from telegram import BotCommand, Update
from telegram.request import HTTPXRequest
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bot.config import get_settings
from bot.database.db import DatabaseManager
from bot.handlers import (
    about_handler,
    base64_handler,
    batch_handler,
    broadcast_handler,
    callback_router_handler,
    color_handler,
    compare_handler,
    country_handler,
    crypto_handler,
    dialcodes_handler,
    dns_handler,
    email_handler,
    epoch_handler,
    forex_handler,
    hash_handler,
    headers_handler,
    help_handler,
    ip_handler,
    jwt_handler,
    language_handler,
    menu_handler,
    password_handler,
    ping_handler,
    port_handler,
    privacy_handler,
    qr_handler,
    qrwifi_handler,
    sample_handler,
    secscan_handler,
    start_handler,
    stats_handler,
    subdomains_handler,
    text_lookup_handler,
    unshorten_handler,
    uuid_handler,
)
from bot.services.cache import MemoryCache
from bot.services.phone_lookup import PhoneLookupService
from bot.services.providers.phonenumbers_provider import PhonenumbersProvider
from bot.utils.logger import setup_logging
from bot.utils.rate_limit import RateLimiter


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler preventing stack traces from leaking to end users."""
    logger = logging.getLogger("phone_intel_bot")
    logger.error("Uncaught exception while handling update: %s", context.error, exc_info=True)

    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ <b>An unexpected error occurred.</b>\n"
                "The incident has been logged. Please try again later.",
                parse_mode="HTML",
            )
        except Exception:
            pass


async def post_init(application: Application) -> None:
    """Set up bot command menu on startup."""
    commands = [
        BotCommand("menu", "🎛️ Master Toolkit Dashboard"),
        BotCommand("start", "Start the bot & quick overview"),
        BotCommand("ip", "🌐 IP Geolocation & ASN Lookup"),
        BotCommand("dns", "🔗 DNS Records Explorer"),
        BotCommand("email", "📧 Email & Disposable Validator"),
        BotCommand("unshorten", "🛡️ URL Expander & Anti-Phishing"),
        BotCommand("qr", "📲 Generate Custom QR Code"),
        BotCommand("qrwifi", "📶 Generate Wi-Fi Connect QR"),
        BotCommand("crypto", "🪙 Live Crypto Prices (USD/INR)"),
        BotCommand("forex", "💱 Real-Time Currency Converter"),
        BotCommand("password", "🔑 High-Entropy Password Generator"),
        BotCommand("hash", "🔐 MD5/SHA-256 Hash Digest"),
        BotCommand("country", "🌍 Country Dialling Code Search"),
        BotCommand("compare", "⚖️ Compare Two Phone Numbers"),
        BotCommand("help", "📖 Full Commands Guide"),
    ]
    await application.bot.set_my_commands(commands)
    logger = logging.getLogger("phone_intel_bot")
    logger.info("Multi-Tool bot command menu configured successfully with v2.0 commands")


def build_application() -> Application:
    """Configure and build the telegram Application."""
    settings = get_settings()
    logger = setup_logging(settings.log_level)

    if not settings.bot_token:
        logger.critical("BOT_TOKEN is not set in environment or .env file. Exiting.")
        sys.exit(1)

    logger.info("Initializing All-in-One Multi-Tool Intelligence Bot (v2.0)...")

    # Initialize shared components
    db = DatabaseManager(settings.database_path)
    cache = MemoryCache(default_ttl=settings.cache_ttl_seconds)
    provider = PhonenumbersProvider()
    lookup_service = PhoneLookupService(provider=provider, cache=cache)
    rate_limiter = RateLimiter(max_requests=settings.rate_limit_per_minute, window_seconds=60)

    # Custom request settings with generous timeouts for high latency networks
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )

    # Build Application
    app = (
        ApplicationBuilder()
        .token(settings.bot_token)
        .request(request)
        .post_init(post_init)
        .build()
    )

    # Store shared instances in bot_data
    app.bot_data["db"] = db
    app.bot_data["lookup_service"] = lookup_service
    app.bot_data["rate_limiter"] = rate_limiter
    app.bot_data["settings"] = settings

    # --- Core & Menu Handlers ---
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("menu", menu_handler))
    app.add_handler(CommandHandler("tools", menu_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("language", language_handler))
    app.add_handler(CommandHandler("privacy", privacy_handler))
    app.add_handler(CommandHandler("about", about_handler))

    # --- Phone & Telecom Handlers ---
    app.add_handler(CommandHandler("country", country_handler))
    app.add_handler(CommandHandler("dialcodes", dialcodes_handler))
    app.add_handler(CommandHandler("sample", sample_handler))
    app.add_handler(CommandHandler("compare", compare_handler))
    app.add_handler(CommandHandler("batch", batch_handler))

    # --- IP & Network Intelligence Handlers ---
    app.add_handler(CommandHandler("ip", ip_handler))
    app.add_handler(CommandHandler("ping", ping_handler))
    app.add_handler(CommandHandler("headers", headers_handler))
    app.add_handler(CommandHandler("port", port_handler))

    # --- Domain, DNS & Web OSINT Handlers ---
    app.add_handler(CommandHandler("dns", dns_handler))
    app.add_handler(CommandHandler("unshorten", unshorten_handler))
    app.add_handler(CommandHandler("subdomains", subdomains_handler))
    app.add_handler(CommandHandler("secscan", secscan_handler))

    # --- Email Intelligence Handlers ---
    app.add_handler(CommandHandler("email", email_handler))

    # --- Crypto, Hashes & Dev Handlers ---
    app.add_handler(CommandHandler("hash", hash_handler))
    app.add_handler(CommandHandler("base64", base64_handler))
    app.add_handler(CommandHandler("password", password_handler))
    app.add_handler(CommandHandler("uuid", uuid_handler))
    app.add_handler(CommandHandler("jwt", jwt_handler))
    app.add_handler(CommandHandler("epoch", epoch_handler))
    app.add_handler(CommandHandler("color", color_handler))

    # --- Markets & Forex Handlers ---
    app.add_handler(CommandHandler("crypto", crypto_handler))
    app.add_handler(CommandHandler("forex", forex_handler))

    # --- QR Code Studio Handlers ---
    app.add_handler(CommandHandler("qr", qr_handler))
    app.add_handler(CommandHandler("qrwifi", qrwifi_handler))

    # --- Admin Handlers ---
    app.add_handler(CommandHandler("stats", stats_handler))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))

    # --- Callback Query Handler for Interactive Buttons ---
    app.add_handler(CallbackQueryHandler(callback_router_handler))

    # --- Text Message Handler (Auto-routes phone queries) ---
    app.add_handler(
        MessageHandler(
            filters.TEXT & (~filters.COMMAND),
            text_lookup_handler,
        )
    )

    # Register Global Error Handler
    app.add_error_handler(error_handler)

    return app


async def run_bot() -> None:
    """Async main routine to initialize DB and run polling."""
    settings = get_settings()
    logger = setup_logging(settings.log_level)

    # Initialize SQLite database
    db = DatabaseManager(settings.database_path)
    await db.initialize()

    # Build application
    app = build_application()

    admin_count = len(settings.admin_ids)
    logger.info(
        "Multi-Tool Bot startup v2.0: Default Region=%s, Admin Count=%d, Rate Limit=%d/min",
        settings.default_region or "None",
        admin_count,
        settings.rate_limit_per_minute,
    )

    # Run polling
    async with app:
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        logger.info("Multi-Tool Bot v2.0 is active and polling for updates...")

        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, stop_event.set)
            except NotImplementedError:
                pass

        await stop_event.wait()
        logger.info("Shutdown signal received. Stopping bot gracefully...")
        await app.updater.stop()
        await app.stop()
        logger.info("Bot shutdown completed.")


def main() -> None:
    """Synchronous entry point."""
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()
