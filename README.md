# 📱 Telegram Phone Number Intelligence Bot

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Framework: python-telegram-bot](https://img.shields.io/badge/telegram-v21%2B-blue)](https://python-telegram-bot.org/)
[![Validation: libphonenumber](https://img.shields.io/badge/validation-Google_libphonenumber-green)](https://github.com/google/libphonenumber)

A fast, secure, and production-ready Telegram bot that accepts international telephone numbers and returns legitimate, publicly available phone number metadata.

Built with **Python 3.12+**, **`python-telegram-bot` (v21+ Async)**, **Google's `libphonenumber` (`phonenumbers`)**, **Pydantic v2**, **`aiosqlite`**, and **in-memory TTL caching**.

---

## 📑 Table of Contents

1. [Features](#1-features)
2. [Architecture & Design](#2-architecture--design)
3. [Installation & Requirements](#3-installation--requirements)
4. [Telegram BotFather Setup](#4-telegram-botfather-setup)
5. [Environment Configuration](#5-environment-configuration)
6. [Local Development](#6-local-development)
7. [Production Deployment (Systemd / Background)](#7-production-deployment-no-docker)
8. [Bot Commands & Interaction Flow](#8-bot-commands--interaction-flow)
9. [Privacy Principles & Ethical Limitations](#9-privacy-principles--ethical-limitations)
10. [Troubleshooting](#10-troubleshooting)
11. [Testing & Quality Assurance](#11-testing--quality-assurance)

---

## 1. Features

- 🌍 **International Parsing & Validation**: Accurate validation using Google's libphonenumber standard.
- 📱 **Number Type Classification**: Identifies Mobile, Landline (Fixed Line), VoIP, Toll Free, Premium Rate, Pager, UAN, and Voicemail.
- 🏢 **Carrier & Telecom Metadata**: Retrieves original network operator allocation where publicly available.
- 📍 **Geographical Region & Timezones**: Displays country, geographic region/state, and applicable timezones.
- 🌐 **Format Standardization**: Formats numbers into standardized **E.164**, **International**, and **National** conventions.
- ⚡ **Instant Response & UI**: Instantaneous search feedback (`🔎 Checking...`) followed by a clean HTML report with inline buttons.
- 🔒 **Privacy-by-Design**: Strictly zero storage of raw phone numbers. Automatic masking in server logs (`+91******3210`).
- 🛡️ **Per-User Rate Limiting**: In-memory sliding window rate limiting to prevent spam and denial of service.
- 🚀 **High Performance Caching**: In-memory TTL caching for identical queries.
- 📊 **Administrator Analytics**: Aggregated `/stats` command for authorized admins showing total lookups, unique users, and top queried countries (without revealing user phone numbers).

---

## 2. Architecture & Design

The bot follows a modular, decoupled architecture adhering to clean separation of concerns:

```
phone-intel-bot/
├── bot/
│   ├── __init__.py
│   ├── main.py                     # Application entry point, lifecycle, and polling
│   ├── config.py                   # Pydantic Settings & environment validation
│   ├── handlers/                   # Telegram event handlers
│   │   ├── __init__.py
│   │   ├── start.py                # /start command & welcome screen
│   │   ├── help.py                 # /help usage instructions
│   │   ├── privacy.py              # /privacy policy & data handling principles
│   │   ├── about.py                # /about bot info & tech stack
│   │   ├── admin.py                # /stats admin telemetry report
│   │   └── lookup.py               # Text message lookup & inline callback router
│   ├── services/                   # Business logic & intelligence layer
│   │   ├── __init__.py
│   │   ├── phone_lookup.py         # Lookup orchestrator & cache integration
│   │   ├── formatter.py            # HTML report generators & escape helpers
│   │   ├── cache.py                # Async in-memory key-value cache with TTL
│   │   └── providers/              # Extensible provider interface
│   │       ├── __init__.py
│   │       ├── base.py             # PhoneMetadata & PhoneLookupProvider ABC
│   │       └── phonenumbers_provider.py  # Libphonenumber offline metadata engine
│   ├── utils/                      # Helper utilities
│   │   ├── __init__.py
│   │   ├── validators.py           # Input sanitization, length, and format checks
│   │   ├── rate_limit.py           # Per-user sliding window rate limiter
│   │   └── logger.py               # Masking logger filter (no raw numbers in logs)
│   └── database/                   # Anonymous telemetry database
│       ├── __init__.py
│       └── db.py                   # Async SQLite storage for aggregated metrics
├── tests/                          # Pytest suite
│   ├── __init__.py
│   ├── test_phone_lookup.py        # Metadata validation tests across countries
│   ├── test_validators.py          # Input boundary & sanitization tests
│   ├── test_rate_limit.py          # Rate limiter tests
│   ├── test_formatter.py           # HTML output & escaping tests
│   └── test_db.py                  # Database operations & aggregate stats tests
├── .env.example                    # Environment configuration template
├── .gitignore
├── requirements.txt                # Production & test dependencies
├── README.md                       # Comprehensive guide & documentation
└── LICENSE                         # MIT License
```

### Extensibility Pattern:
External lookup providers (e.g. carrier HLR APIs, Numverify, Twilio Lookup) can be added cleanly by implementing the `PhoneLookupProvider` abstract base class in `bot/services/providers/` without altering core bot logic.

---

## 3. Installation & Requirements

### Prerequisites
- Python **3.12+**
- Git
- Telegram account

### Clone and Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/yourusername/phone-intel-bot.git
cd phone-intel-bot

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Telegram BotFather Setup

1. Open Telegram and search for [@BotFather](https://t.me/BotFather).
2. Send `/newbot` and follow the prompts to choose a name and username.
3. BotFather will provide an HTTP API token (e.g. `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).
4. *(Optional)* Set description and commands with BotFather:
   ```
   start - Start the bot & overview
   help - How to use the bot
   privacy - Privacy principles & data handling
   about - System architecture & info
   stats - Admin statistics (Admin only)
   ```

---

## 5. Environment Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```ini
# =====================================================================
# Telegram Phone Number Intelligence Bot Configuration
# =====================================================================

# Telegram Bot Token from @BotFather (Required)
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ

# Telegram User ID(s) of authorized admins for /stats command (Optional)
# Get your ID from @userinfobot. Multiple IDs can be comma-separated: 123456789,987654321
ADMIN_ID=123456789

# Path to SQLite database file for anonymous telemetry
DATABASE_PATH=bot.db

# Default ISO 3166-1 alpha-2 fallback country code (Optional: e.g. IN, US, GB)
# When set, numbers entered without '+' prefix will assume this country.
# When unset, the bot prompts users to specify a country code.
DEFAULT_REGION=

# Rate limit: Maximum lookups allowed per user per minute
RATE_LIMIT_PER_MINUTE=10

# In-memory cache TTL for identical queries in seconds (default: 600 = 10 minutes)
CACHE_TTL_SECONDS=600

# Logging level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Environment mode: production or development
ENVIRONMENT=production
```

---

## 6. Local Development

Run the bot directly using Python:

```bash
# Ensure virtual environment is active
source .venv/bin/activate

# Run the bot
python -m bot.main
```

You will see the startup banner:
```
[2026-08-21 12:00:00] [INFO] [phone_intel_bot:52] Logging initialized with privacy masking enabled at level INFO
[2026-08-21 12:00:00] [INFO] [bot.database.db:58] Database initialized successfully at bot.db
[2026-08-21 12:00:01] [INFO] [phone_intel_bot:122] Bot startup: Default Region=None, Admin Count=1, Rate Limit=10/min
[2026-08-21 12:00:01] [INFO] [phone_intel_bot:131] Bot is active and polling for updates...
```

To stop the bot cleanly, press `Ctrl + C`.

---

## 7. Production Deployment (No Docker)

### Option A: Running as a systemd Service (Recommended)

1. Create a systemd service file `/etc/systemd/system/phone-intel-bot.service`:

```ini
[Unit]
Description=Telegram Phone Number Intelligence Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/phone-intel-bot
ExecStart=/usr/bin/python3 -m bot.main
Restart=always
RestartSec=5
EnvironmentFile=/root/phone-intel-bot/.env

# Standard output and error logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

2. Enable and start the service:
```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable service to start automatically on system boot
sudo systemctl enable phone-intel-bot

# Start the bot service
sudo systemctl start phone-intel-bot

# Check status
sudo systemctl status phone-intel-bot

# View real-time logs
sudo journalctl -u phone-intel-bot -f
```

---

### Option B: Running in Background with nohup

```bash
cd /root/phone-intel-bot
nohup python3 -m bot.main > bot.log 2>&1 &
```

View output:
```bash
tail -f bot.log
```

---

### Option C: Running inside tmux or screen

```bash
# Start a new tmux session
tmux new -s phone-bot

# Run the bot
cd /root/phone-intel-bot
python3 -m bot.main

# Detach from session: Press Ctrl+B then D
# Reattach anytime:
tmux attach -t phone-bot
```

---

## 8. Bot Commands & Interaction Flow

### Available Commands

| Command | Permission | Description |
| :--- | :--- | :--- |
| `/start` | Public | Welcome screen, capabilities, and quick search button |
| `/help` | Public | Detailed usage guide, format rules, and examples |
| `/privacy` | Public | Explains data handling, zero-log policy, and limitations |
| `/about` | Public | Technology stack, architecture, and security features |
| `/stats` | **Admin Only** | Shows total lookups, unique users, and top queried regions |

### Example User Interaction

1. User sends: `+91 98765 43210`
2. Bot instantly responds: `🔎 Checking phone number metadata...`
3. Bot updates message with structured report:

```
📱 PHONE LOOKUP REPORT
━━━━━━━━━━━━━━━━━━

🔢 Number
+91 98765 43210

🌍 Country
India

📞 Country Code
+91

📱 Type
Mobile

✅ Valid Format
✅ Yes (Valid number format)

🔎 Possible
✅ Yes

🏢 Carrier
Not available

📍 General Region
India

🕐 Timezone
Asia/Calcutta

🌐 International
+91 98765 43210

☎️ National
09876543210

━━━━━━━━━━━━━━━━━━
ℹ️ Public metadata only • Not proof of ownership or live status
```

4. Attached Inline Buttons:
   `[ 🔄 Check Another ]` `[ ℹ️ Help ]`

---

## 9. Privacy Principles & Ethical Limitations

### Critical Distinction: Metadata vs Identity vs Live Status

This bot is built with strict privacy and legal compliance safeguards:

> [!IMPORTANT]
> 1. **No Personal Identity Data**: The bot does **not** disclose subscriber names, home addresses, WhatsApp accounts, social media profiles, or SIM KYC information.
> 2. **No Live Status**: "Valid format" confirms structural validity under ITU-T E.164 rules; it does **not** guarantee an active SIM or active cellular connection.
> 3. **No Live GPS Location**: "Region" reflects telecom prefix geographic boundaries, never a handset's physical real-time GPS coordinates.
> 4. **Zero Raw Phone Storage**: Raw query numbers are never permanently stored in SQLite or application databases.
> 5. **Log Masking**: All server logs automatically redact numbers (e.g. `+91******3210`).

---

## 10. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `BOT_TOKEN is not set` | Missing token in `.env` | Ensure `.env` exists and contains valid `BOT_TOKEN=...`. |
| `Too many requests` | User exceeded rate limit | Default limit is 10 queries/min. Wait 60s or adjust `RATE_LIMIT_PER_MINUTE`. |
| `Missing country code` | User omitted `+` sign | Numbers should start with `+` (e.g. `+1...`, `+91...`) or configure `DEFAULT_REGION=IN`. |
| `Unauthorized for /stats` | User ID not in `ADMIN_ID` | Check your Telegram ID with `@userinfobot` and add it to `ADMIN_ID` in `.env`. |
| `ModuleNotFoundError` | Dependencies not installed | Run `pip install -r requirements.txt` in your active virtual environment. |

---

## 11. Testing & Quality Assurance

Run the automated test suite with `pytest`:

```bash
# Run all tests
pytest -v

# Run with coverage report
pytest --cov=bot tests/
```

### Test Coverage Breakdown
- `test_phone_lookup.py`: Validates Indian (+91), US (+1), UK (+44), Toll-Free (+1-800), possible numbers, unassigned ranges, and in-memory TTL caching.
- `test_validators.py`: Verifies length bounds (max 50 chars), empty string handling, unicode normalization, and illegal character rejection.
- `test_rate_limit.py`: Verifies sliding window rate limiter, per-user isolation, and quota reset.
- `test_formatter.py`: Verifies HTML entity escaping (XSS prevention), report templates, and admin telemetry formatting.
- `test_db.py`: Verifies SQLite table generation, anonymous telemetry insertion, and aggregate stats calculations.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
