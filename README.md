<div align="center">

# 📱 Phone Intel Bot

### Open-source Telegram intelligence & developer utility suite

A modular, privacy-conscious Telegram bot for **public phone metadata, network diagnostics, DNS/web analysis, email checks, QR generation, cryptographic utilities, and market data**.

<p>
  <a href="https://github.com/Rishav7324/phone-intel-bot/stargazers"><img src="https://img.shields.io/github/stars/Rishav7324/phone-intel-bot?style=for-the-badge&logo=github" alt="GitHub stars"></a>
  <a href="https://github.com/Rishav7324/phone-intel-bot/network/members"><img src="https://img.shields.io/github/forks/Rishav7324/phone-intel-bot?style=for-the-badge&logo=github" alt="GitHub forks"></a>
  <a href="https://github.com/Rishav7324/phone-intel-bot/issues"><img src="https://img.shields.io/github/issues/Rishav7324/phone-intel-bot?style=for-the-badge&logo=github" alt="Issues"></a>
  <a href="https://github.com/Rishav7324/phone-intel-bot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/Rishav7324/phone-intel-bot?style=for-the-badge" alt="MIT License"></a>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram">
  <img src="https://img.shields.io/badge/Async-First-6C63FF?style=for-the-badge" alt="Async first">
  <img src="https://img.shields.io/badge/Open%20Source-MIT-111827?style=for-the-badge" alt="Open source">
</p>

<p>
  <a href="#-quick-start">Quick Start</a> ·
  <a href="#-features">Features</a> ·
  <a href="#-architecture">Architecture</a> ·
  <a href="#-contributing">Contributing</a> ·
  <a href="#-security--privacy">Security</a>
</p>

> **Metadata ≠ identity.** Phone Intel Bot works with public/technical metadata. It does not claim to reveal private subscriber identity, SIM ownership, live GPS location, private accounts, or message activity.

</div>

---

## ✨ Highlights

- 🧩 **Modular architecture** — handlers, services, providers, utilities, and persistence are separated.
- 🔌 **Provider abstraction** — phone lookup providers share a common interface and can be extended.
- ⚡ **Async-first** — built around `python-telegram-bot`, async I/O, and `aiosqlite`.
- 📴 **Local phone metadata** — the default phone provider uses Google's libphonenumber metadata through Python's `phonenumbers` package. fileciteturn28file0
- 🔐 **Privacy-aware logging** — sensitive lookup input is designed to be masked rather than written to normal logs.
- 🚦 **Rate limiting + caching** — repeated requests can be controlled and cached.
- 🧪 **Test suite included** — pytest + pytest-asyncio are part of the development dependencies. fileciteturn26file0
- 🪶 **Lightweight deployment** — default setup uses SQLite rather than requiring a separate database server.
- 🛠️ **Useful beyond phone lookups** — DNS, network, email, QR, crypto, and developer utilities live behind the same Telegram interface.

---

## 🧰 Features

| Module | Capabilities |
|---|---|
| 📱 **Phone Intelligence** | Parse, validate, classify, format and inspect public telecom metadata |
| 🌐 **IP & Network** | IP metadata, headers, latency, reverse DNS and targeted port checks |
| 🔎 **DNS & Web** | DNS records, redirect tracing, CT subdomain discovery, security headers |
| 📧 **Email** | Syntax validation, MX checks and disposable-domain detection |
| 📲 **QR Studio** | Text/URL, Wi-Fi and contact QR workflows |
| 🔐 **Crypto & Dev** | Hashing, Base64, passwords, UUIDs, JWT parsing and timestamps |
| 📈 **Market Data** | Crypto prices and foreign-exchange conversion |

---

## 📱 Phone Intelligence

The phone module uses the open-source **libphonenumber** metadata engine through the `phonenumbers` Python package. The current implementation extracts technical metadata locally rather than pretending to provide private identity information. fileciteturn28file0

### Available metadata

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

### Important limitations

> A number being **valid** according to libphonenumber does not prove that a SIM is active, that a person owns the number, or that the number is currently reachable.

This distinction is deliberately documented because **metadata lookup is not subscriber identification**.

---

## 🌐 Network & Web Utilities

### IP / network

- IP geolocation metadata
- ISP / ASN information
- Reverse DNS
- VPN / proxy / datacenter indicators
- Latency and TCP/DNS timing checks
- HTTP response-header inspection
- Targeted TCP port checks

### DNS / domain

- A / AAAA
- MX
- TXT
- NS
- CNAME
- SOA
- URL redirect-chain inspection
- Certificate Transparency based subdomain discovery
- Security-header grading

> These utilities are intended for **defensive diagnostics, troubleshooting, and systems you own or are authorized to test**.

---

## 🧰 Developer Utilities

```text
/hash       → MD5 / SHA-1 / SHA-256 / SHA-512
/base64     → Encode / decode Base64
/password   → Generate secure random passwords
/uuid       → UUID generation
/jwt        → Decode JWT header/payload metadata
/epoch      → Unix timestamp ↔ UTC / IST
/color      → HEX → RGB preview
/qr         → Generate QR codes
/qrwifi     → Generate Wi-Fi QR codes
```

---

## 🏗️ Architecture

```text
                         Telegram User
                              │
                              ▼
                  ┌───────────────────────┐
                  │   python-telegram-bot │
                  │    Update / Callback   │
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
                  │       Services        │
                  │ logic / cache / flow │
                  └───────┬───────┬──────┘
                          │       │
              ┌───────────┘       └───────────┐
              ▼                               ▼
    ┌────────────────────┐          ┌────────────────────┐
    │ Provider Layer     │          │ Utility Layer      │
    │ phone / adapters   │          │ validation / rate  │
    │ external metadata  │          │ limiting / logging │
    └──────────┬─────────┘          └────────────────────┘
               │
               ▼
    ┌────────────────────┐
    │ Persistence Layer  │
    │ async SQLite       │
    │ aggregate metrics  │
    └────────────────────┘
```

The repository separates Telegram event handling from business logic and provider implementations. The phone provider follows a common `PhoneLookupProvider` abstraction, allowing future provider adapters without coupling them to Telegram handlers. fileciteturn23file0

---

## 📂 Project Structure

```text
phone-intel-bot/
├── bot/
│   ├── main.py
│   ├── config.py
│   ├── handlers/
│   │   ├── start.py
│   │   ├── help.py
│   │   ├── privacy.py
│   │   ├── about.py
│   │   ├── admin.py
│   │   └── lookup.py
│   ├── services/
│   │   ├── phone_lookup.py
│   │   ├── formatter.py
│   │   ├── cache.py
│   │   └── providers/
│   │       ├── base.py
│   │       └── phonenumbers_provider.py
│   ├── utils/
│   │   ├── validators.py
│   │   ├── rate_limit.py
│   │   └── logger.py
│   └── database/
│       └── db.py
├── tests/
├── .env.example
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start

### Requirements

- Python **3.12+**
- Telegram account
- A bot token from [@BotFather](https://t.me/BotFather)
- Git

### 1. Clone

```bash
git clone https://github.com/Rishav7324/phone-intel-bot.git
cd phone-intel-bot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The repository's dependency set includes Telegram Bot API support, phone metadata, Pydantic settings, async HTTP/database libraries, DNS utilities, QR generation, Pillow, and pytest tooling. fileciteturn26file0

### 4. Configure environment

```bash
cp .env.example .env
```

At minimum, configure your Telegram bot token:

```env
BOT_TOKEN=your_telegram_bot_token
```

Do **not** commit `.env` or secrets to Git.

### 5. Run

```bash
python -m bot.main
```

---

## 🤖 Bot Commands

| Command | Purpose |
|---|---|
| `/start` | Start the bot and show capabilities |
| `/help` | Show usage information |
| `/privacy` | Explain privacy and data handling |
| `/about` | Show project and architecture information |
| `/stats` | Admin-only aggregate statistics |

Additional tools are exposed through the bot's command/lookup interface as documented by each module.

---

## ⚙️ Configuration

The repository provides `.env.example` so configuration can be kept outside source code. The documented configuration includes:

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

Keep credentials, tokens and private infrastructure settings outside Git.

---

## 🧪 Testing

Run the test suite with:

```bash
pytest
```

For a more explicit run:

```bash
pytest -v
```

Async tests are supported through `pytest-asyncio`. fileciteturn26file0

When contributing a feature, add or update tests for the relevant provider, service, validator or utility whenever practical.

---

## 🔐 Security & Privacy

Phone Intel Bot is designed around a **metadata-first** model.

### What it does not claim to provide

- ❌ Subscriber identity
- ❌ SIM/KYC ownership
- ❌ Live GPS location
- ❌ Private WhatsApp/Telegram account information
- ❌ Private messages or call records
- ❌ Guaranteed SIM activity/reachability

### Responsible use

Use network, DNS, port, subdomain and web-analysis functionality only against systems you own or have explicit permission to test.

If you discover a security vulnerability in the project itself, please **do not publish sensitive exploit details immediately**. Open a private security report where available or contact the maintainer through the repository's security/contact channels.

---

## 🧩 Extending the Phone Provider

The project intentionally separates the phone lookup interface from the implementation.

Conceptually:

```python
class PhoneLookupProvider:
    async def lookup(self, phone_number, default_region=None):
        ...
```

A new provider can implement the same interface and be registered without moving provider-specific logic into Telegram handlers.

This makes the project suitable for future adapters such as additional telecom metadata providers while keeping the core architecture stable.

---

## 🗺️ Roadmap

The roadmap is intentionally focused on maintainability and useful open-source contributions:

- [ ] Improve command discoverability and inline UX
- [ ] Expand automated test coverage
- [ ] Add provider health/status reporting
- [ ] Improve structured error handling
- [ ] Add more pluggable metadata providers
- [ ] Add CI for linting + tests
- [ ] Add release/version automation
- [ ] Improve documentation with screenshots and examples
- [ ] Add Docker/compose deployment as an optional path
- [ ] Improve observability without collecting unnecessary personal data

Have an idea? Open an issue and discuss it before making a large architectural change.

---

## 🤝 Contributing

Contributions are welcome.

### Development workflow

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/phone-intel-bot.git
cd phone-intel-bot

# Create a branch
git checkout -b feat/my-improvement

# Create environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Make changes
# Add/update tests
pytest -v

# Commit
git add .
git commit -m "feat: describe your change"

# Push
git push origin feat/my-improvement
```

Then open a Pull Request against `main`.

### Good first contributions

- Documentation improvements
- Tests for existing utilities
- Bug fixes with regression tests
- Better error messages
- New provider adapters
- Performance improvements
- Telegram UX improvements

Please keep pull requests **focused, documented, tested, and backwards-conscious**.

---

## 📋 Pull Request Checklist

Before opening a PR:

- [ ] The change has a clear purpose
- [ ] Existing functionality still works
- [ ] Tests were added/updated where appropriate
- [ ] `pytest -v` passes locally
- [ ] No secrets or credentials were committed
- [ ] Documentation was updated if behavior changed
- [ ] Security/privacy implications were considered
- [ ] The PR is focused on one logical change

---

## 🐛 Bug Reports & Feature Requests

Please use GitHub Issues for:

- reproducible bugs
- feature proposals
- documentation problems
- provider compatibility issues

A useful bug report should include:

1. What you expected
2. What actually happened
3. Python version
4. Operating system
5. Relevant command/input with secrets removed
6. Reproduction steps
7. Error output or logs with sensitive data redacted

---

## 📜 License

This project is released under the **MIT License**. See [`LICENSE`](LICENSE) for the complete license text.

---

## ⭐ Support the Project

If Phone Intel Bot is useful to you:

- ⭐ Star the repository
- 🐛 Report reproducible bugs
- 💡 Suggest improvements
- 🔧 Contribute code or documentation
- 🍴 Fork it and build something useful

Every contribution helps turn a small experiment into a better open-source project.

---

<div align="center">

### Built with Python 🐍 · Telegram 🤖 · Open Source ❤️

**Metadata, not identity. Build responsibly.**

</div>
