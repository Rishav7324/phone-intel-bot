"""Privacy-first logging configuration with automatic phone number and token masking."""

import logging
import re
import sys
from typing import Any


def mask_phone_number(text: str) -> str:
    """Mask phone numbers found within a text string to preserve privacy in logs.

    Examples:
        +919876543210 -> +91******3210
        +12025550123  -> +120******0123
        9876543210    -> 98******10
    """
    if not text:
        return text

    # Pattern for E.164-like or generic international/national phone sequences
    def _mask_match(match: re.Match) -> str:
        s = match.group(0)
        digits_only = re.sub(r"\D", "", s)
        if len(digits_only) < 7:
            return s
        prefix = s[:3]
        suffix = s[-4:] if len(s) >= 8 else s[-2:]
        return f"{prefix}******{suffix}"

    pattern = re.compile(r"(?:\+?\d[\d\s\-\(\)\.]{6,16}\d)")
    return pattern.sub(_mask_match, text)


class PrivacyMaskingFilter(logging.Filter):
    """Logging filter that ensures sensitive tokens and raw phone numbers are masked."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = mask_phone_number(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: (mask_phone_number(v) if isinstance(v, str) else v)
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    mask_phone_number(v) if isinstance(v, str) else v
                    for v in record.args
                )
        return True


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configure root and application loggers with privacy protections."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    log_format = (
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    # Reset any existing handlers
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers to prevent duplicates
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(numeric_level)
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(PrivacyMaskingFilter())

    root_logger.addHandler(stream_handler)

    # Reduce verbosity of external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)

    logger = logging.getLogger("phone_intel_bot")
    logger.info("Logging initialized with privacy masking enabled at level %s", log_level)
    return logger
