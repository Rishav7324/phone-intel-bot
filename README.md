<div align="center">

# 📱 Phone Intel Bot

### Telegram Multi-Tool for Public Phone Metadata, Network Utilities & Developer Tools

A privacy-conscious, modular Telegram bot that turns a single chat into a practical toolkit for **telephone-number metadata, IP/network diagnostics, DNS & web checks, email validation, QR generation, cryptographic utilities, and market data**.

<p>
  <a href="https://github.com/Rishav7324/phone-intel-bot"><img src="https://img.shields.io/github/stars/Rishav7324/phone-intel-bot?style=for-the-badge&logo=github" alt="GitHub stars"></a>
  <a href="https://github.com/Rishav7324/phone-intel-bot/issues"><img src="https://img.shields.io/github/issues/Rishav7324/phone-intel-bot?style=for-the-badge" alt="GitHub issues"></a>
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12+"></img>
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Bot"></img>
  <img src="https://img.shields.io/github/license/Rishav7324/phone-intel-bot?style=for-the-badge" alt="MIT License"></img>
</p>

<p>
  <strong>Metadata ≠ identity.</strong> The project intentionally focuses on publicly available technical metadata and does not claim to reveal private subscriber information, live GPS location, SIM ownership, or account activity.
</p>

</div>

---

## ✨ Why Phone Intel Bot?

Instead of maintaining separate scripts for phone parsing, DNS checks, QR generation, hashing, and network diagnostics, this project puts them behind one Telegram interface.

The architecture is deliberately **modular and provider-oriented** so new data providers or utilities can be added without rewriting the bot's core flow.

### Core principles

- 🔐 **Privacy-aware** — raw phone numbers are masked in logs and the documented design avoids storing raw lookup numbers as permanent telemetry.
- 🧩 **Modular** — handlers, services, providers, utilities, and persistence are separated.
- ⚡ **Async-first** — built around `python-telegram-bot`, async providers, and `aiosqlite`.
- 📴 **Offline phone metadata** — the primary phone provider uses the local `phonenumbers` metadata engine rather than requiring an HLR lookup API.
- 🧪 **Testable** — project includes a dedicated `pytest` test suite.
- 🔌 **Extensible** — phone lookup providers implement a common provider abstraction.
- 🪶 **Lightweight** — no Docker or external database is required for the default setup.

---

## 🧰 Feature Matrix

| Module | What it provides | Example |
|---|---|---|
| 📱 Phone Intelligence | Parsing, validation, number type, country, region, carrier metadata, timezone, formatting | `/lookup +91...` |
| 🌐 IP & Network | IP metadata, headers, latency/ping, selected port checks | `/ip`, `/ping`, `/headers` |
| 🔎 DNS & Web | DNS records, redirect tracing, CT-based subdomain discovery, security-header checks | `/dns`, `/unshorten`, `/subdomains` |
| 📧 Email | Syntax validation, MX checks, disposable-email detection | `/email user@example.com` |
| 🧾 QR Studio | Text/URL QR, Wi-Fi QR, contact/vCard workflows | `/qr`, `/qrwifi` |
| 🔐 Crypto & Dev | Hashes, Base64, passwords, UUIDs, JWT parsing, epoch conversion | `/hash`, `/jwt`, `/uuid` |
| 📈 Market Tools | Crypto prices and FX conversion | `/crypto`, `/forex` |

---

# 📱 Phone Intelligence

The phone module is based on Google's open-source **libphonenumber** metadata through the Python `phonenumbers` package.

It can determine technical metadata such as:

- Country and calling code
- Possible vs. valid number status
- Mobile / landline / VoIP / toll-free / premium-rate classification
- General geographic description where metadata exists
- Carrier metadata where available
- Timezone metadata
- E.164, international, national and RFC 3966 formats
- Telecom allocation risk heuristics
- Emergency-number classification
- Country flag, capital and currency metadata
- Optional WhatsApp/Telegram chat-link formatting

The provider implementation is local and follows a common `PhoneLookupProvider` interface, making it possible to add alternative providers later. fileciteturn28file0

> **Important:** a valid number according to libphonenumber does **not** prove that a SIM is active, that a person owns the number, or that the number is currently reachable.

---

# 🌐 Network & Web Utilities

### IP utilities

- IP geolocation metadata
- ISP / ASN information
- Reverse DNS information
- VPN / proxy / datacenter indicators
- Latency and TCP/DNS timing checks
- HTTP response-header inspection
- Targeted TCP port checks

### DNS & domain utilities

- A / AAAA
- MX
- TXT
- NS
- CNAME
- SOA
- URL redirect-chain inspection
- Certificate Transparency based subdomain discovery
- Security-header grading

These utilities are intended for **defensive diagnostics, troubleshooting, and authorized security testing**.

---

# 📧 Email Intelligence

The email module provides technical deliverability-oriented checks without attempting to access private mailboxes:

- RFC-style address validation
- MX record checks
- Disposable/burner-domain detection
- Basic domain-level diagnostics

---

# 🧰 Developer Toolkit

The bot also doubles as a compact developer utility toolbox:

```text
/hash       → MD5 / SHA-1 / SHA-256 / SHA-512
/base64     → Encode / decode Base64
/password   → Generate cryptographically secure passwords
/uuid       → UUID generation
/jwt        → Decode JWT header/payload metadata
/epoch      → Unix timestamp ↔ UTC/IST
/color      → HEX → RGB preview
/qr         → Generate QR codes
/qrwifi     → Generate Wi-Fi QR codes
```

---

# 🏗️ Architecture

```text
                         Telegram User
                              │
                              ▼
                  ┌───────────────────────┐
                  │ python-telegram-bot  │
                  │   Update / Callback   │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │       Handlers        │
                  │ commands / callbacks │
                  └───────────┬───────────┘
                              │
                              ▼
                  ┌───────────────────────┐
                  │      Services        │
                  │ business logic/cache │
                  └───────┬───────┬──────┘
                          │       │
             ┌────────────┘       └─────────────┐
             ▼                                  ▼
   ┌────────────────────┐              ┌───────────────────┐
   │ Provider Layer     │              │ Utility Layer     │
   │ phone / external   │              │ validation / rate │
   │ metadata adapters  │              │ limiting / logs   │
   └─────────┬──────────┘              └───────────────────┘
             │
             ▼
   ┌────────────────────┐
   │ Data / Persistence │
   │ async SQLite       │
   │ aggregated metrics │
   └────────────────────┘
```

The repository separates Telegram event handling from business logic and provider implementations. The current phone provider is a local `phonenumbers` implementation, while the abstraction allows future provider adapters without changing the rest of the application. fileciteturn23file0

---

# 📂 Project Structure

```text
phone-intel-bot/
│
├── bot/
│   ├── main.py
│   ├── config.py
│   │
│   ├── handlers/
│   │   ├── start.py
│   │   ├── help.py
│   │   ├── privacy.py
│   │   ├── about.py
│   │   ├── admin.py
│   │   └── lookup.py
│   │
│   ├── services/
│   │   ├── phone_lookup.py
│   │   ├── formatter.py
│   │   ├── cache.py
│   │   └── providers/
│   │       ├── base.py
│   │       └── phonenumbers_provider.py
│   │
│   ├── utils/
│   │   ├── validators.py
│   │   ├── rate_limit.py
│   │   └── logger.py
│   │
│   └── database/
│       └── db.py
│
├── tests/
├── .env.example
├── requirements.txt
├── LICENSE
└── README.md
```

---

# 🛠️ Tech Stack

| Technology | Role |
|---|---|
| **Python 3.12+** | Application runtime |
| **python-telegram-bot 21+** | Telegram interface |
| **phonenumbers** | Phone parsing and metadata |
| **Pydantic Settings** | Configuration validation |
| **httpx** | Async HTTP requests |
| **aiosqlite** | Async SQLite persistence |
| **dnspython** | DNS operations |
| **qrcode + Pillow** | QR generation and image handling |
| **pytest + pytest-asyncio** | Testing |

The current dependency set is intentionally compact and includes dedicated testing packages. fileciteturn26file0

---

# 🚀 Quick Start

## 1. Clone

```bash
git clone https://github.com/Rishav7324/phone-intel-bot.git
cd phone-intel-bot
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

## 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configure environment

```bash
cp .env.example .env
```

Then set at minimum:

```env
BOT_TOKEN=your_telegram_bot_token
```

Optional configuration includes admin IDs, default region, rate limits, cache TTL, database path, log level, and environment mode.

## 5. Start the bot

```bash
python -m bot.main
```

---

# 🤖 Telegram Setup

1. Open Telegram and search for **@BotFather**.
2. Run `/newbot`.
3. Choose the bot name and username.
4. Copy the generated token.
5. Put it in `.env`:

```env
BOT_TOKEN=123456789:your-token
```

6. Start the application.

The project also exposes informational commands such as `/help`, `/privacy`, `/about`, and an admin-only `/stats` flow according to the current implementation/documentation. fileciteturn23file0

---

# 💻 Example Usage

### Phone metadata

```text
+91 98765 43210
```

The bot can return a structured report containing technical metadata such as:

```text
📱 PHONE REPORT
━━━━━━━━━━━━━━━━━━━━

🌍 Country       India
📞 Calling Code  +91
📱 Type          Mobile
✅ Valid         Yes
🔎 Possible      Yes
🏢 Carrier       Metadata if available
📍 Region        Metadata if available
🕐 Timezone      Asia/Calcutta

Formats
• E.164
• International
• National
• RFC 3966

⚠️ Metadata only — not proof of ownership or live status.
```

### Other examples

```text
/dns example.com
/ip 1.1.1.1
/ping example.com
/headers https://example.com
/email user@example.com
/qr https://github.com/Rishav7324/phone-intel-bot
/hash hello world
/base64 enc hello
/uuid
/epoch
```

---

# 🔐 Privacy & Security Model

Privacy is a core part of this project rather than an afterthought.

### What it does

- Processes telephone numbers as **technical metadata inputs**.
- Uses local `phonenumbers` metadata for the primary phone lookup path.
- Applies input validation and rate limiting.
- Uses masked logging for phone-number related diagnostics.
- Supports aggregated telemetry through SQLite.

### What it does NOT claim to provide

- ❌ Subscriber name lookup
- ❌ SIM/KYC ownership information
- ❌ Live GPS location
- ❌ Private WhatsApp/Telegram account data
- ❌ Private social-media accounts
- ❌ Guaranteed SIM activity or reachability

> **Rule of thumb:** if a result would require private subscriber records, a carrier-only database, or unauthorized access to an account/device, this project should not pretend that public metadata can provide it.

---

# ⚠️ Responsible Use

Use the network, DNS, port, email, and OSINT utilities only against systems, domains, accounts, or data that you own or are explicitly authorized to test.

Do not use this project for harassment, stalking, credential attacks, unauthorized scanning, privacy invasion, or attempts to identify private individuals.

The project is designed around **public metadata and defensive diagnostics**, not covert surveillance.

---

# 🧪 Testing

Install development dependencies from `requirements.txt`, then run:

```bash
pytest
```

For async tests:

```bash
pytest -v
```

The repository includes tests covering phone lookup behavior, validation, rate limiting, formatting, and database operations according to its documented structure. fileciteturn23file0

---

# 🔌 Extending the Phone Provider

The phone lookup layer uses a provider abstraction.

A new provider can implement the shared interface rather than modifying Telegram handlers or presentation logic:

```python
class PhoneLookupProvider:
    async def lookup(self, phone_number: str, default_region=None):
        ...
```

Conceptually:

```text
Telegram Handler
      │
      ▼
Lookup Service
      │
      ▼
PhoneLookupProvider
      │
      ├── Local phonenumbers provider
      │
      └── Future provider adapters
```

This keeps external integrations optional and the core application testable.

---

# ⚙️ Configuration

The `.env.example` file supports configuration for:

```env
BOT_TOKEN=
ADMIN_ID=
DATABASE_PATH=bot.db
DEFAULT_REGION=
RATE_LIMIT_PER_MINUTE=10
CACHE_TTL_SECONDS=600
LOG_LEVEL=INFO
ENVIRONMENT=production
```

Recommended production behavior:

- Use a strong secret/token configuration.
- Never commit `.env`.
- Keep admin IDs restricted.
- Keep logging at `INFO` unless debugging.
- Review rate limits before exposing the bot publicly.
- Run the bot under a dedicated non-root service account where possible.

---

# 📦 Production Deployment

The bot can run as a normal Python process and can be supervised with tools such as **systemd**, `tmux`, `screen`, or another process manager.

Example:

```bash
python -m bot.main
```

For a long-running deployment, prefer a process supervisor that can:

- restart failed processes
- isolate environment variables
- rotate logs
- run under a non-root user
- provide health/uptime monitoring

---

# 🗺️ Roadmap

Potential future improvements:

- [ ] Plugin registry for additional lookup providers
- [ ] Better structured command discovery
- [ ] More comprehensive integration tests
- [ ] Persistent distributed rate limiting
- [ ] Redis-compatible cache adapter
- [ ] Webhook deployment mode
- [ ] Docker/OCI deployment profile
- [ ] Better provider health reporting
- [ ] Configurable feature permissions
- [ ] More defensive security-header diagnostics
- [ ] Optional localization / multilingual responses

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Add or update tests where appropriate.
4. Keep provider-specific logic isolated.
5. Run the test suite.
6. Open a pull request with a clear description.

```bash
git checkout -b feat/my-improvement
pytest
git commit -m "feat: improve phone metadata provider"
git push origin feat/my-improvement
```

---

# 📄 License

Released under the **MIT License**.

See [`LICENSE`](LICENSE) for the full license text.

---

<div align="center">

### 🔎 Public metadata. Practical tools. Privacy-aware engineering.

Built by **[Rishav Raj](https://github.com/Rishav7324)**

⭐ If this project is useful, consider giving it a star.

</div>
