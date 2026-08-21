"""Telegram Bot Handlers."""

from .start import start_handler
from .help import help_handler
from .privacy import privacy_handler
from .about import about_handler
from .admin import stats_handler
from .country import country_handler
from .language import language_handler
from .batch import batch_handler
from .broadcast import broadcast_handler
from .sample import sample_handler
from .compare import compare_handler
from .dialcodes import dialcodes_handler
from .menu_handler import menu_handler
from .ip_handler import ip_handler, ping_handler, headers_handler, port_handler
from .domain_handler import dns_handler, unshorten_handler, subdomains_handler, secscan_handler
from .email_handler import email_handler
from .crypto_handler import (
    hash_handler,
    base64_handler,
    password_handler,
    uuid_handler,
    jwt_handler,
    epoch_handler,
    color_handler,
)
from .market_handler import crypto_handler, forex_handler
from .qr_handler import qr_handler, qrwifi_handler
from .lookup import text_lookup_handler, callback_router_handler

__all__ = [
    "start_handler",
    "menu_handler",
    "help_handler",
    "privacy_handler",
    "about_handler",
    "stats_handler",
    "country_handler",
    "language_handler",
    "batch_handler",
    "broadcast_handler",
    "sample_handler",
    "compare_handler",
    "dialcodes_handler",
    "ip_handler",
    "ping_handler",
    "headers_handler",
    "port_handler",
    "dns_handler",
    "unshorten_handler",
    "subdomains_handler",
    "secscan_handler",
    "email_handler",
    "hash_handler",
    "base64_handler",
    "password_handler",
    "uuid_handler",
    "jwt_handler",
    "epoch_handler",
    "color_handler",
    "crypto_handler",
    "forex_handler",
    "qr_handler",
    "qrwifi_handler",
    "text_lookup_handler",
    "callback_router_handler",
]
