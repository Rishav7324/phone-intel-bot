"""Main entry point for Telegram Phone Number Intelligence Bot."""

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
    batch_handler,
    broadcast_handler,
    callback_router_handler,
    country_handler,
    help_handler,
    language_handler,
    privacy_handler,
    start_handler,
    stats_handler,
    text_lookup_handler,
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
        BotCommand("start", "Start the bot & quick overview"),
        BotCommand("help", "Usage guide & examples"),
        BotCommand("country", "Lookup country dialling codes & info"),
        BotCommand("batch", "Multi-number batch analysis guide"),
        BotCommand("language", "Switch English / Hindi language"),
        BotCommand("privacy", "Privacy policy & data principles"),
        BotCommand("about", "Bot info & tech stack"),
    ]
    await application.bot.set_my_commands(commands)
    logger = logging.getLogger("phone_intel_bot")
    logger.info("Bot command menu configured successfully")


def build_application() -> Application:
    """Configure and build the telegram Application."""
    settings = get_settings()
    logger = setup_logging(settings.log_level)

    if not settings.bot_token:
        logger.critical("BOT_TOKEN is not set in environment or .env file. Exiting.")
        sys.exit(1)

    logger.info("Initializing Upgraded Phone Intelligence Bot...")

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

    # Register Public Command Handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("country", country_handler))
    app.add_handler(CommandHandler("batch", batch_handler))
    app.add_handler(CommandHandler("language", language_handler))
    app.add_handler(CommandHandler("privacy", privacy_handler))
    app.add_handler(CommandHandler("about", about_handler))

    # Register Admin Command Handlers
    app.add_handler(CommandHandler("stats", stats_handler))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))

    # Register Callback Query Handler for inline buttons
    app.add_handler(CallbackQueryHandler(callback_router_handler))

    # Register Text Message Handler (exclude commands)
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
        "Bot startup: Default Region=%s, Admin Count=%d, Rate Limit=%d/min",
        settings.default_region or "None",
        admin_count,
        settings.rate_limit_per_minute,
    )

    # Run polling
    async with app:
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        logger.info("Bot is active and polling for updates...")

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
