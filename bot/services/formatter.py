"""HTML Message formatting service for standard and internationalized reports."""

import html
from typing import Any, List, Optional
from bot.database.db import AdminStats
from bot.services.providers.base import NumberStatus, PhoneMetadata
from bot.utils.country_data import CountryInfo


def escape(text: Any) -> str:
    """Safely escape text for Telegram HTML parse mode."""
    if text is None:
        return ""
    return html.escape(str(text), quote=True)


def format_country_report(info: CountryInfo) -> str:
    """Format single country dialling code profile."""
    return (
        f"{info.flag} <b>COUNTRY CALLING CODE PROFILE</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🌍 <b>Country:</b> {escape(info.name_en)} ({escape(info.name_hi)})\n"
        f"📞 <b>Calling Code:</b> <code>{escape(info.calling_code)}</code>\n"
        f"🔤 <b>ISO Alpha-2:</b> <code>{escape(info.iso2)}</code>\n"
        f"🔤 <b>ISO Alpha-3:</b> <code>{escape(info.iso3)}</code>\n"
        f"🏛️ <b>Capital:</b> {escape(info.capital)}\n"
        f"💵 <b>Currency:</b> {escape(info.currency)}\n"
        f"🗣️ <b>Official Language:</b> {escape(info.languages)}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"💡 <i>To check a phone number for {info.name_en}, send:</i> <code>{info.calling_code} ...</code>"
    )


def format_batch_report(results: List[PhoneMetadata], lang: str = "en") -> str:
    """Format a summary report for multiple phone numbers."""
    total = len(results)
    valid_count = sum(1 for r in results if r.is_valid)

    if lang == "hi":
        header = f"📊 <b>बैच फोन लुकअप रिपोर्ट ({total} नंबर)</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        stats = f"<b>कुल विश्लेषित:</b> {total} | <b>मान्य प्रारूप:</b> {valid_count}/{total}\n\n"
    else:
        header = f"📊 <b>BATCH LOOKUP REPORT ({total} Numbers)</b>\n━━━━━━━━━━━━━━━━━━\n\n"
        stats = f"<b>Analyzed:</b> {total} | <b>Valid Formats:</b> {valid_count}/{total}\n\n"

    items = []
    for idx, r in enumerate(results, start=1):
        num_str = r.international_format or r.input_number
        flag = r.flag_emoji or "🌐"
        status_icon = "✅" if r.is_valid else ("⚠️" if r.is_possible else "❌")
        carrier_str = f" • {r.carrier}" if r.carrier and r.carrier != "Not available" else ""
        items.append(
            f"<b>{idx}.</b> {flag} <code>{escape(num_str)}</code>\n"
            f"   {status_icon} {escape(r.country_name)} ({escape(r.number_type)}){escape(carrier_str)}"
        )

    footer = "\n\n━━━━━━━━━━━━━━━━━━\nℹ️ <i>Click individual numbers to perform detailed single lookups.</i>"
    return header + stats + "\n".join(items) + footer


def format_lookup_report(metadata: PhoneMetadata, lang: str = "en") -> str:
    """Generate HTML report for phone number lookup."""
    num = escape(metadata.international_format or metadata.national_format or metadata.input_number)
    flag = metadata.flag_emoji or "🌐"
    country = escape(metadata.country_name)
    calling_code = escape(metadata.country_calling_code_str or "N/A")
    number_type = escape(metadata.number_type)
    carrier = escape(metadata.carrier)
    region = escape(metadata.region_description)
    timezones = escape(", ".join(metadata.timezones))
    e164 = escape(metadata.e164_format or "N/A")
    intl = escape(metadata.international_format or "N/A")
    national = escape(metadata.national_format or "N/A")
    risk_level = escape(metadata.risk_level)
    risk_desc = escape(metadata.risk_description)

    valid_str = "✅ Yes (Valid ITU format)" if metadata.is_valid else "❌ No (Invalid / Unallocated)"
    possible_str = "✅ Yes" if metadata.is_possible else "❌ No"

    if metadata.is_emergency:
        risk_level = "🚨 Emergency Service"
        risk_desc = "Recognized National Emergency Hotline"

    if lang == "hi":
        return (
            f"📱 <b>फोन नंबर इंटेलिजेंस रिपोर्ट</b> {flag}\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🔢 <b>फोन नंबर</b>\n<code>{num}</code>\n\n"
            f"🌍 <b>देश (Country)</b>\n{flag} {country}\n\n"
            f"📞 <b>कॉलिंग कोड</b>\n{calling_code}\n\n"
            f"📱 <b>प्रकार (Type)</b>\n{number_type}\n\n"
            f"🛡️ <b>सुरक्षा / रिस्क स्तर</b>\n{risk_level} <i>({risk_desc})</i>\n\n"
            f"✅ <b>मान्य प्रारूप</b>\n{valid_str}\n\n"
            f"🏢 <b>ऑपरेटर (Carrier)</b>\n{carrier}\n\n"
            f"📍 <b>क्षेत्र (Region)</b>\n{region}\n\n"
            f"🕐 <b>समय क्षेत्र (Timezone)</b>\n{timezones}\n\n"
            f"🌐 <b>अंतर्राष्ट्रीय प्रारूप (E.164)</b>\n<code>{e164}</code>\n\n"
            f"☎️ <b>राष्ट्रीय प्रारूप</b>\n<code>{national}</code>\n\n"
            "━━━━━━━━━━━━━━━━━━\n"
            "ℹ️ <i>केवल सार्वजनिक मेटाडेटा • सिम मालिक का नाम कानूनन निजी है</i>"
        )

    return (
        f"📱 <b>PHONE LOOKUP REPORT</b> {flag}\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔢 <b>Number</b>\n<code>{num}</code>\n\n"
        f"🌍 <b>Country</b>\n{flag} {country}\n\n"
        f"📞 <b>Country Code</b>\n{calling_code}\n\n"
        f"📱 <b>Type</b>\n{number_type}\n\n"
        f"🛡️ <b>Risk Assessment</b>\n{risk_level} <i>({risk_desc})</i>\n\n"
        f"✅ <b>Valid Format</b>\n{valid_str}\n\n"
        f"🔎 <b>Possible</b>\n{possible_str}\n\n"
        f"🏢 <b>Carrier</b>\n{carrier}\n\n"
        f"📍 <b>General Region</b>\n{region}\n\n"
        f"🕐 <b>Timezone</b>\n{timezones}\n\n"
        f"🌐 <b>International</b>\n<code>{intl}</code>\n\n"
        f"☎️ <b>National</b>\n<code>{national}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "ℹ️ <i>Public metadata only • Not proof of ownership or live status</i>"
    )


def format_start_message(lang: str = "en") -> str:
    """Return welcome message for /start command."""
    if lang == "hi":
        return (
            "🎛️ <b>ऑल-इन-वन मल्टी-टूल बॉट (Multi-Tool Suite v2.0)</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "नमस्ते! यह टेलीग्राम का सबसे शक्तिशाली और सुरक्षित <b>Multi-Utility Toolkit</b> है।\n\n"
            "🚀 <b>उपलब्ध मुख्य टूल्स:</b>\n"
            "• 📱 <b>Phone Intel:</b> कोई भी नंबर भेजें (जैसे <code>+91 98765 43210</code>)\n"
            "• 🌐 <b>IP & Network:</b> <code>/ip &lt;address&gt;</code>, <code>/ping &lt;host&gt;</code>\n"
            "• 🔗 <b>Domain & DNS:</b> <code>/dns &lt;domain&gt;</code>, <code>/unshorten &lt;link&gt;</code>\n"
            "• 📧 <b>Email Validator:</b> <code>/email &lt;address&gt;</code>\n"
            "• 📲 <b>QR Studio:</b> <code>/qr &lt;text&gt;</code>, <code>/qrwifi &lt;SSID&gt; &lt;Pass&gt;</code>\n"
            "• 🔐 <b>Crypto & Security:</b> <code>/password</code>, <code>/hash</code>, <code>/jwt</code>\n"
            "• 🪙 <b>Markets:</b> <code>/crypto</code>, <code>/forex</code>\n\n"
            "🎛️ सभी टूल्स को एक साथ देखने के लिए <b>/menu</b> दबाएं!\n"
            "📖 पूरी कमांड लिस्ट के लिए <b>/help</b> दबाएं।"
        )

    return (
        "🎛️ <b>All-in-One Multi-Tool Intelligence Suite (v2.0)</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome! Your versatile Telegram assistant for <b>OSINT, Network, Telecom, Dev Utilities, & Security Tools</b>.\n\n"
        "🚀 <b>Core Tool Highlights:</b>\n"
        "• 📱 <b>Phone Intel:</b> Send any number directly (e.g. <code>+91 98765 43210</code>)\n"
        "• 🌐 <b>IP & Network:</b> <code>/ip &lt;address&gt;</code>, <code>/ping &lt;host&gt;</code>\n"
        "• 🔗 <b>Domain & DNS:</b> <code>/dns &lt;domain&gt;</code>, <code>/unshorten &lt;link&gt;</code>\n"
        "• 📧 <b>Email Validator:</b> <code>/email &lt;address&gt;</code>\n"
        "• 📲 <b>QR Studio:</b> <code>/qr &lt;text&gt;</code>, <code>/qrwifi &lt;SSID&gt; &lt;Pass&gt;</code>\n"
        "• 🔐 <b>Crypto & Hashes:</b> <code>/password</code>, <code>/hash</code>, <code>/jwt</code>\n"
        "• 🪙 <b>Crypto & Forex:</b> <code>/crypto</code>, <code>/forex</code>\n\n"
        "🎛️ Tap <b>/menu</b> for the interactive visual dashboard!\n"
        "📖 Tap <b>/help</b> for the complete command directory."
    )


def format_help_message(lang: str = "en") -> str:
    """Return complete categorized documentation for /help command."""
    if lang == "hi":
        return (
            "📖 <b>मल्टी-टूल बॉट — पूरी कमांड सूची (Complete Command Guide)</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "📱 <b>1. फोन और टेलीकॉम टूल्स:</b>\n"
            "• डायरेक्ट नंबर भेजें (उदा. <code>+91 98765 43210</code>)\n"
            "• <code>/country &lt;name/code&gt;</code> — देश का कॉलिंग कोड व विवरण\n"
            "• <code>/dialcodes</code> — दुनिया के सभी देशों के कोड्स की सूची\n"
            "• <code>/sample &lt;country&gt;</code> — टेस्ट/सैंपल फोन नंबर जनरेटर\n"
            "• <code>/compare &lt;n1&gt; &lt;n2&gt;</code> — दो नंबरों की आपस में तुलना\n"
            "• <code>/batch</code> — एक साथ कई नंबर जांचने का तरीका\n\n"
            "🌐 <b>2. IP और नेटवर्क टूल्स:</b>\n"
            "• <code>/ip &lt;IP/domain&gt;</code> — Geolocation, ISP, ASN और VPN रिस्क\n"
            "• <code>/ping &lt;host&gt;</code> — DNS व TCP लेटेंसी टेस्ट (ms में)\n"
            "• <code>/headers &lt;url&gt;</code> — HTTP रिस्पॉन्स हेडर व सर्वर\n"
            "• <code>/port &lt;host&gt; &lt;port&gt;</code> — पोर्ट खुला (Open) है या बंद\n\n"
            "🔗 <b>3. डोमेन, DNS व वेब OSINT:</b>\n"
            "• <code>/dns &lt;domain&gt;</code> — A, AAAA, MX, TXT, NS रिकॉर्ड्स\n"
            "• <code>/unshorten &lt;url&gt;</code> — छोटे लिंक्स (bit.ly) की असली लिंक खोजें\n"
            "• <code>/subdomains &lt;domain&gt;</code> — सबडोमेन्स की खोज (CT logs)\n"
            "• <code>/secscan &lt;domain&gt;</code> — वेबसाइट सुरक्षा स्कोर (A+ से F)\n\n"
            "📧 <b>4. ईमेल टूल्स:</b>\n"
            "• <code>/email &lt;address&gt;</code> — ईमेल वैधता, MX सर्वर व Temp-Mail जांच\n\n"
            "📲 <b>5. क्यूआर कोड स्टूडियो:</b>\n"
            "• <code>/qr &lt;text/url&gt;</code> — कस्टम QR कोड फोटो बनाएं\n"
            "• <code>/qrwifi &lt;SSID&gt; &lt;Pass&gt; [WPA]</code> — वाई-फाई डायरेक्ट कनेक्ट QR\n\n"
            "🔐 <b>6. डेवलपर्स व सुरक्षा टूल्स:</b>\n"
            "• <code>/hash &lt;text&gt;</code> — MD5, SHA-1, SHA-256, SHA-512\n"
            "• <code>/base64 &lt;enc/dec&gt; &lt;text&gt;</code> — Base64 एनकोड/डिकोड\n"
            "• <code>/password [length]</code> — मजबूत सुरक्षित पासवर्ड बनाएं\n"
            "• <code>/uuid</code> — UUID v4 / v1 जनरेटर\n"
            "• <code>/jwt &lt;token&gt;</code> — JWT टोकन हेडर व पेलोड डिकोडर\n"
            "• <code>/epoch [timestamp]</code> — Unix टाइम ↔ दिनांक कनवर्टर\n"
            "• <code>/color &lt;HEX&gt;</code> — कलर कोड कनवर्टर व कलर फोटो\n\n"
            "🪙 <b>7. क्रिप्टो और फॉरेक्स मार्केट्स:</b>\n"
            "• <code>/crypto [coins]</code> — BTC, ETH, SOL, TON के लाइव रेट्स\n"
            "• <code>/forex &lt;amt&gt; &lt;FROM&gt; &lt;TO&gt;</code> — रियल-टाइम करेंसी कनवर्टर\n\n"
            "⚙️ <b>8. सेटिंग्स और मेनू:</b>\n"
            "• <code>/menu</code> — इंटरएक्टिव टूलकिट डैशबोर्ड\n"
            "• <code>/language</code> — भाषा बदलें (English / हिन्दी)\n"
            "• <code>/privacy</code> — गोपनीयता नीति (Zero Storage)\n"
            "• <code>/about</code> — बॉट की जानकारी व तकनीक\n\n"
            "━━━━━━━━━━━━━━━━━━"
        )

    return (
        "📖 <b>MULTI-TOOL MASTER DIRECTORY — ALL COMMANDS (v2.0)</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "📱 <b>1. Phone & Telecom Intelligence:</b>\n"
        "• Send any phone number directly (e.g. <code>+91 98765 43210</code>)\n"
        "• <code>/country &lt;name/code&gt;</code> — Country dialling code, currency, flag\n"
        "• <code>/dialcodes</code> — Browse global world dialling directory\n"
        "• <code>/sample &lt;country&gt;</code> — Generate valid ITU sample test numbers\n"
        "• <code>/compare &lt;n1&gt; &lt;n2&gt;</code> — Side-by-side number comparison\n"
        "• <code>/batch</code> — Multi-number batch lookup syntax\n\n"
        "🌐 <b>2. IP & Network Intelligence:</b>\n"
        "• <code>/ip &lt;IP/domain&gt;</code> — Geolocation, ISP, ASN, and Proxy/VPN check\n"
        "• <code>/ping &lt;host&gt;</code> — Measure DNS resolution & TCP handshake latency\n"
        "• <code>/headers &lt;url&gt;</code> — Inspect HTTP response headers & server\n"
        "• <code>/port &lt;host&gt; &lt;port&gt;</code> — Test if a TCP port is open or closed\n\n"
        "🔗 <b>3. Domain, DNS & Web OSINT:</b>\n"
        "• <code>/dns &lt;domain&gt;</code> — Query A, AAAA, MX, TXT, NS, CNAME records\n"
        "• <code>/unshorten &lt;url&gt;</code> — Trace redirect chains & expand short links\n"
        "• <code>/subdomains &lt;domain&gt;</code> — Discover subdomains via CT logs\n"
        "• <code>/secscan &lt;domain&gt;</code> — Audit HTTP security headers (A+ to F grade)\n\n"
        "📧 <b>4. Email Intelligence:</b>\n"
        "• <code>/email &lt;address&gt;</code> — Syntax validity, MX servers, & burner mail check\n\n"
        "📲 <b>5. QR Code Studio:</b>\n"
        "• <code>/qr &lt;text or url&gt;</code> — Generate custom high-res QR code image\n"
        "• <code>/qrwifi &lt;SSID&gt; &lt;Pass&gt; [WPA]</code> — Generate Wi-Fi instant connect QR\n\n"
        "🔐 <b>6. Crypto, Hashes & Dev Utilities:</b>\n"
        "• <code>/hash &lt;text&gt;</code> — Compute MD5, SHA-1, SHA-256, SHA-512\n"
        "• <code>/base64 &lt;enc/dec&gt; &lt;text&gt;</code> — Base64 Encoder / Decoder\n"
        "• <code>/password [len]</code> — Generate high-entropy secure random password\n"
        "• <code>/uuid</code> — Generate UUID v4 & UUID v1\n"
        "• <code>/jwt &lt;token&gt;</code> — Decode JSON Web Token header & payload\n"
        "• <code>/epoch [ts]</code> — Convert Unix timestamp ↔ UTC / IST\n"
        "• <code>/color &lt;HEX&gt;</code> — Convert HEX to RGB & render visual color swatch\n\n"
        "🪙 <b>7. Live Markets & Forex:</b>\n"
        "• <code>/crypto [coins]</code> — Live BTC, ETH, SOL, TON rates in USD & INR\n"
        "• <code>/forex &lt;amt&gt; &lt;FROM&gt; &lt;TO&gt;</code> — Real-time currency exchange rates\n\n"
        "⚙️ <b>8. Master Menu & Settings:</b>\n"
        "• <code>/menu</code> or <code>/tools</code> — Interactive visual dashboard\n"
        "• <code>/language</code> — Switch interface language (English / हिन्दी)\n"
        "• <code>/privacy</code> — Zero-log privacy principles\n"
        "• <code>/about</code> — Bot architecture & technology stack\n\n"
        "━━━━━━━━━━━━━━━━━━"
    )


def format_privacy_message(lang: str = "en") -> str:
    """Return privacy policy for /privacy command."""
    if lang == "hi":
        return (
            "🔒 <b>गोपनीयता नीति और डेटा सुरक्षा (Privacy Policy)</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "यह बॉट सख्त <b>Privacy-by-Design</b> सिद्धांतों पर आधारित है:\n\n"
            "1. <b>Zero Raw Number Storage:</b>\n"
            "हम आपके द्वारा भेजे गए फोन नंबर, ईमेल या आईपी को कभी भी डेटाबेस में सेव या स्टोर नहीं करते।\n\n"
            "2. <b>Anonymous Telemetry:</b>\n"
            "सिर्फ अज्ञात आंकड़े (जैसे किस देश का कोड सर्च हुआ, कुल अनुरोध) सिस्टम परफॉर्मेंस के लिए रखे जाते हैं।\n\n"
            "3. <b>No Private Data Access:</b>\n"
            "यह बॉट किसी सरकारी रिकॉर्ड, आधार/केवाईसी या प्राइवेट डेटाबेस को एक्सेस नहीं करता।\n\n"
            "4. <b>Server Log Redaction:</b>\n"
            "सर्वर लॉग्स में सभी संवेदनशील नंबर स्वतः मास्क (उदा. <code>+91******3210</code>) हो जाते हैं।"
        )

    return (
        "🔒 <b>Privacy Policy & Data Principles</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "This bot is built strictly upon <b>privacy-by-design</b> principles:\n\n"
        "1. <b>Zero Raw Query Storage:</b>\n"
        "We never save, store, or log raw phone numbers, email addresses, or IP addresses in our database or permanent disks.\n\n"
        "2. <b>Anonymous Aggregates:</b>\n"
        "Usage statistics only capture anonymous aggregates (timestamp, country code, validity boolean) for performance metrics.\n\n"
        "3. <b>No Private Data Access:</b>\n"
        "This bot does not query government databases, SIM KYC registries, WhatsApp/Telegram accounts, or personal address books.\n\n"
        "4. <b>Log Redaction:</b>\n"
        "All server logs automatically mask sensitive digit sequences (e.g. <code>+91******3210</code>) to protect user queries."
    )


def format_about_message(lang: str = "en") -> str:
    """Return bot architecture and technology info for /about command."""
    if lang == "hi":
        return (
            "ℹ️ <b>ऑल-इन-वन मल्टी-टूल बॉट के बारे में (About v2.0)</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "एक आधुनिक, हाई-स्पीड और सुरक्षित ऑल-इन-वन टेलीग्राम बॉट जो 20 से अधिक OSINT, नेटवर्क, टेलीकॉम और डेवलपर टूल्स प्रदान करता है।\n\n"
            "🛠️ <b>शामिल 8 टूल सूट्स:</b>\n"
            "1. 📱 <b>Phone Intel:</b> ITU प्रारूप, ऑपरेटर, रिस्क स्कोर, vCard, QR\n"
            "2. 🌐 <b>IP & Network:</b> जियोलोकेशन, ISP, ASN, लेटेंसी पिंग, पोर्ट चेक\n"
            "3. 🔗 <b>Domain & DNS:</b> DNS रिकॉर्ड्स, URL Unshorten, सबडोमेन्स, सिक्योरिटी स्कैन\n"
            "4. 📧 <b>Email Validator:</b> MX रिकॉर्ड्स और टेम्प-मेल डिटेक्टर\n"
            "5. 📲 <b>QR Code Studio:</b> कस्टम QR और वाई-फाई कनेक्ट कोड्स\n"
            "6. 🔐 <b>Crypto & Security:</b> MD5/SHA256 हैश, Base64, पासवर्ड, JWT\n"
            "7. 🪙 <b>Live Markets:</b> रियल-टाइम क्रिप्टो व फॉरेक्स कनवर्टर\n"
            "8. 🇮🇳 <b>द्विभाषी सपोर्ट:</b> अंग्रेजी व हिन्दी (Bilingual UI)\n\n"
            "💻 <b>टेक स्टैक:</b>\n"
            "Python 3.12+, python-telegram-bot v21+ (Async), Google libphonenumber, dnspython, Pillow, qrcode, aiosqlite, Pydantic v2."
        )

    return (
        "ℹ️ <b>About Multi-Tool Intelligence Suite (v2.0)</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "A fast, secure, and production-grade All-in-One Telegram Bot providing over 20+ OSINT, Telecom, Network, Developer, and Security utilities.\n\n"
        "🛠️ <b>Included 8 Tool Suites:</b>\n"
        "1. 📱 <b>Phone Intel:</b> ITU metadata, carrier allocation, risk scoring, vCard, QR\n"
        "2. 🌐 <b>IP & Network:</b> Geolocation, ISP, ASN, ping latency, port accessibility\n"
        "3. 🔗 <b>Domain & DNS:</b> DNS explorer, anti-phishing URL expander, subdomains, secscan\n"
        "4. 📧 <b>Email Validator:</b> Format validation, MX records, disposable burner filter\n"
        "5. 📲 <b>QR Code Studio:</b> Custom text/URL QR codes & Wi-Fi auto-connect\n"
        "6. 🔐 <b>Crypto & Security:</b> MD5/SHA-256 hashes, Base64, passwords, JWT decoder\n"
        "7. 🪙 <b>Markets & Forex:</b> Live crypto rates (USD/INR) & currency exchange\n"
        "8. 🌐 <b>Bilingual UI:</b> Full English & Hindi localization with instant toggle\n\n"
        "💻 <b>Tech Stack:</b>\n"
        "Python 3.12+, python-telegram-bot v21+ (Async), Google libphonenumber, dnspython, Pillow, qrcode, aiosqlite, Pydantic v2."
    )


def format_admin_stats(stats: AdminStats) -> str:
    """Return formatted admin statistics report."""
    top_countries_text = ""
    if stats.top_countries:
        for idx, (country, count) in enumerate(stats.top_countries, start=1):
            top_countries_text += f"\n  {idx}. <code>{escape(country)}</code>: {count:,}"
    else:
        top_countries_text = "\n  <i>No lookups recorded yet.</i>"

    return (
        "📊 <b>SYSTEM TELEMETRY & ANALYTICS</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 <b>Total Unique Users:</b> {stats.total_users:,}\n"
        f"🔍 <b>Total Lookups Executed:</b> {stats.total_lookups:,}\n"
        f"✅ <b>Valid Formats:</b> {stats.valid_lookups:,}\n"
        f"❌ <b>Invalid Queries:</b> {stats.invalid_lookups:,}\n\n"
        f"🌍 <b>Top Queried Regions:</b>{top_countries_text}\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔒 <i>Zero phone numbers or user identities stored in telemetry</i>"
    )


def format_rate_limit_message(retry_after: int, lang: str = "en") -> str:
    """Return rate limit warning message."""
    if lang == "hi":
        return (
            f"⏳ <b>अनुरोध सीमा पार हो गई (Rate Limit Exceeded)</b>\n\n"
            f"सिस्टम सुरक्षा के लिए कृपया <b>{retry_after} सेकंड</b> प्रतीक्षा करें।"
        )
    return (
        f"⏳ <b>Rate Limit Exceeded</b>\n\n"
        f"You are sending queries too quickly. Please wait <b>{retry_after} seconds</b> before trying again."
    )
