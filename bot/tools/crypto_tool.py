"""Crypto, Hashing, and Developer utilities: Hashes, Base64, Passwords, UUIDs, JWT, Epoch, and Color."""

import base64
import datetime
import hashlib
import io
import json
import secrets
import string
import time
import uuid
from typing import Dict, Any, Optional, Tuple
from PIL import Image


def generate_hashes(text: str) -> Dict[str, str]:
    """Compute standard cryptographic hash digests for an input string."""
    data = text.encode("utf-8")
    return {
        "md5": hashlib.md5(data).hexdigest(),
        "sha1": hashlib.sha1(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "sha512": hashlib.sha512(data).hexdigest(),
    }


def handle_base64(action: str, text: str) -> Tuple[bool, str]:
    """Encode or decode Base64 strings."""
    try:
        if action.lower() in ("enc", "encode"):
            encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
            return True, encoded
        elif action.lower() in ("dec", "decode"):
            decoded = base64.b64decode(text.encode("utf-8")).decode("utf-8", errors="replace")
            return True, decoded
        else:
            return False, "Invalid action. Use <code>/base64 enc &lt;text&gt;</code> or <code>/base64 dec &lt;text&gt;</code>."
    except Exception as e:
        return False, f"Base64 error: {e}"


def generate_password(length: int = 16, include_symbols: bool = True) -> str:
    """Generate a high-entropy cryptographically secure random password."""
    length = max(8, min(64, length))
    chars = string.ascii_letters + string.digits
    if include_symbols:
        chars += "!@#$%^&*()-_=+[]{}<>?"

    # Ensure at least one lowercase, uppercase, digit, symbol
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()-_=+") if include_symbols else secrets.choice(string.digits),
    ]
    for _ in range(length - len(password)):
        password.append(secrets.choice(chars))

    secrets.SystemRandom().shuffle(password)
    return "".join(password)


def generate_uuids() -> Dict[str, str]:
    """Generate UUID v4 and v1."""
    return {
        "uuid4": str(uuid.uuid4()),
        "uuid1": str(uuid.uuid1()),
        "hex": uuid.uuid4().hex,
    }


def decode_jwt(jwt_token: str) -> Dict[str, Any]:
    """Parse and decode JWT header and payload without verifying signature."""
    parts = jwt_token.strip().split(".")
    if len(parts) != 3:
        return {"success": False, "error": "Invalid JWT format. A valid token must contain 3 parts separated by dots."}

    def _pad_and_decode(segment: str) -> Dict[str, Any]:
        padded = segment + "=" * ((4 - len(segment) % 4) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("utf-8"))
        return json.loads(raw.decode("utf-8"))

    try:
        header = _pad_and_decode(parts[0])
        payload = _pad_and_decode(parts[1])

        # Parse timestamps if present
        exp_ts = payload.get("exp")
        exp_str = datetime.datetime.fromtimestamp(exp_ts, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC") if exp_ts else "None"

        iat_ts = payload.get("iat")
        iat_str = datetime.datetime.fromtimestamp(iat_ts, datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC") if iat_ts else "None"

        return {
            "success": True,
            "header": header,
            "payload": payload,
            "algorithm": header.get("alg", "Unknown"),
            "type": header.get("typ", "JWT"),
            "expires_at": exp_str,
            "issued_at": iat_str,
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to decode token: {e}"}


def convert_epoch(raw_val: Optional[str] = None) -> Dict[str, Any]:
    """Convert between Unix epoch timestamps and human date formats."""
    now_ts = time.time()

    if not raw_val or not raw_val.strip():
        # Current time
        target_ts = int(now_ts)
    else:
        cleaned = raw_val.strip()
        if cleaned.isdigit():
            target_ts = int(cleaned)
        else:
            try:
                # Try parsing standard ISO/date
                dt = datetime.datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
                target_ts = int(dt.timestamp())
            except Exception:
                target_ts = int(now_ts)

    dt_utc = datetime.datetime.fromtimestamp(target_ts, datetime.timezone.utc)
    dt_ist = dt_utc + datetime.timedelta(hours=5, minutes=30)  # IST timezone offset

    return {
        "epoch": target_ts,
        "utc_str": dt_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "ist_str": dt_ist.strftime("%Y-%m-%d %H:%M:%S IST (+05:30)"),
        "iso8601": dt_utc.isoformat(),
        "relative": f"{int(now_ts - target_ts)} seconds ago" if now_ts >= target_ts else f"in {int(target_ts - now_ts)} seconds",
    }


def convert_color(hex_input: str) -> Tuple[Dict[str, Any], io.BytesIO]:
    """Convert HEX color code to RGB, HSL and generate preview image swatch."""
    clean_hex = hex_input.strip().lstrip("#").upper()
    if len(clean_hex) == 3:
        clean_hex = "".join(c * 2 for c in clean_hex)

    if len(clean_hex) != 6 or not all(c in "0123456789ABCDEF" for c in clean_hex):
        clean_hex = "3B82F6"  # Default fallback blue

    r = int(clean_hex[0:2], 16)
    g = int(clean_hex[2:4], 16)
    b = int(clean_hex[4:6], 16)

    # Generate Image Swatch
    img = Image.new("RGB", (300, 150), (r, g, b))
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    bio.name = f"color_{clean_hex}.png"

    return {
        "hex": f"#{clean_hex}",
        "rgb": f"rgb({r}, {g}, {b})",
        "r": r,
        "g": g,
        "b": b,
    }, bio
