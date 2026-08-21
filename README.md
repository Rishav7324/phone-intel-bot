# 🎛️ All-in-One Telegram Multi-Tool & Intelligence Suite (v2.0)

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Framework: python-telegram-bot](https://img.shields.io/badge/telegram-v21%2B-blue)](https://python-telegram-bot.org/)
[![Validation: libphonenumber](https://img.shields.io/badge/validation-Google_libphonenumber-green)](https://github.com/google/libphonenumber)

A fast, secure, and production-ready all-in-one Telegram Bot providing **Phone Intelligence**, **IP & Network Tools**, **DNS & Web OSINT**, **Email Deliverability & Burner Checks**, **QR Code Studio**, **Cryptographic & Developer Utilities**, and **Live Crypto/Forex Trackers**.

---

## 📑 Table of Contents

1. [Multi-Tool Suite Catalog](#1-multi-tool-suite-catalog)
2. [Architecture & Design](#2-architecture--design)
3. [Installation & Requirements](#3-installation--requirements)
4. [Telegram BotFather Setup](#4-telegram-botfather-setup)
5. [Environment Configuration](#5-environment-configuration)
6. [Local & Background Deployment](#6-local--background-deployment)
7. [Commands & Interaction Flow](#7-commands--interaction-flow)
8. [Privacy Principles & Security](#8-privacy-principles--security)
9. [Testing & Quality Assurance](#9-testing--quality-assurance)

---

## 1. Multi-Tool Suite Catalog

### 📱 Suite 1: Phone & Telecom Intelligence
- **ITU Parsing & Formatting**: Real-time validation via Google's `libphonenumber`.
- **Classification & Carrier**: Identifies Mobile, Landline, VoIP, Toll-Free, and network allocations.
- **Telecom Risk Assessment**: Heuristic risk badges (`🟢 Low`, `🟡 Medium (VoIP)`, `🔴 High (Premium Rate)`).
- **Direct Chat Links**: Instant one-tap WhatsApp (`wa.me`) and Telegram (`t.me`) chat actions.
- **Contact QR & vCard**: Generates scannable QR PNG images and `.vcf` contact cards.
- **Batch Analysis (`/batch`)**: Process up to 10 numbers at once with unified summary reports.
- **Dial Code Directory (`/country`, `/dialcodes`)**: World calling codes, emoji flags, currencies, and capitals.
- **Sample Number Generator (`/sample`)**: Valid test numbers for Mobile, Landline, and Toll-Free.
- **Number Comparator (`/compare`)**: Side-by-side comparison of two telephone numbers.

### 🌐 Suite 2: IP & Network Intelligence
- **IP Geolocation (`/ip <address>`)**: Country, City, Region, Zip, ISP, ASN, and Reverse DNS.
- **VPN / Proxy / Cloud Flagging**: Identifies if an IP belongs to a proxy, Tor exit, or datacenter.
- **Latency & Ping Tester (`/ping <host>`)**: Measures DNS resolution and TCP handshake latency in ms.
- **HTTP Headers Analyzer (`/headers <url>`)**: Inspects server type, HSTS, CSP, and response headers.
- **Port Scanner (`/port <host> <port>`)**: Tests if specific TCP ports are open/filtered.

### 🔗 Suite 3: Domain, DNS & Web OSINT
- **DNS Records Explorer (`/dns <domain>`)**: Resolves A, AAAA, MX, TXT, NS, CNAME, SOA records.
- **URL Unshortener (`/unshorten <url>`)**: Traces HTTP redirect chains (bit.ly, t.co, tinyurl) for anti-phishing safety.
- **Subdomain Discovery (`/subdomains <domain>`)**: Queries Certificate Transparency (crt.sh) logs.
- **Security Headers Grader (`/secscan <domain>`)**: Audits CSP, HSTS, X-Frame-Options and scores website security (A+ to F).

### 📧 Suite 4: Email & Burner Mail Detector
- **Email Validator (`/email <address>`)**: RFC 5322 syntax validation and live MX exchange check.
- **Disposable Mail Filter**: Detects 100+ temporary burner email providers (TempMail, 10MinuteMail, Mailinator).

### 📲 Suite 5: QR Code Studio
- **Custom QR Generator (`/qr <text/url>`)**: Generates high-resolution QR codes for links, text, or crypto wallets.
- **Wi-Fi Join QR Generator (`/qrwifi <SSID> <Pass> [WPA]`)**: Generates scannable Wi-Fi login codes.

### 🔐 Suite 6: Hashes, Crypto & Dev Utilities
- **Cryptographic Hashes (`/hash <text>`)**: Computes MD5, SHA-1, SHA-256, and SHA-512 in one view.
- **Base64 Studio (`/base64 enc|dec <text>`)**: Encodes and decodes base64 strings.
- **Password Generator (`/password [length]`)**: High-entropy cryptographically secure random passwords.
- **UUID Generator (`/uuid`)**: Generates UUID v4 (random) and UUID v1 (timestamp).
- **JWT Token Decoder (`/jwt <token>`)**: Parses JWT header, payload, expiration (`exp`), and issued-at (`iat`).
- **Epoch Timestamp Converter (`/epoch [timestamp]`)**: Converts Unix seconds ↔ UTC and Indian Standard Time (IST).
- **Color Previewer (`/color <HEX>`)**: Converts HEX to RGB and renders a visual color swatch preview!

### 📈 Suite 7: Crypto & Forex Trackers
- **Live Crypto Rates (`/crypto [coins]`)**: Bitcoin, Ethereum, Solana, TON, Dogecoin prices in USD & INR via CoinGecko.
- **Forex Calculator (`/forex <amount> <FROM> <TO>`)**: Real-time currency exchange rates.

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
