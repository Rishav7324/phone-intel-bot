"""Market, Crypto & Forex intelligence tools."""

from typing import Dict, Any, List
import httpx

CRYPTO_ID_MAP = {
    "BTC": ("bitcoin", "Bitcoin (BTC)", "🪙"),
    "ETH": ("ethereum", "Ethereum (ETH)", "💎"),
    "SOL": ("solana", "Solana (SOL)", "⚡"),
    "BNB": ("binancecoin", "BNB (BNB)", "🟡"),
    "DOGE": ("dogecoin", "Dogecoin (DOGE)", "🐕"),
    "XRP": ("ripple", "XRP (XRP)", "🌊"),
    "ADA": ("cardano", "Cardano (ADA)", "🔵"),
    "TON": ("the-open-network", "TON (Telegram)", "✈️"),
}


async def get_crypto_prices(coins: List[str] = None) -> Dict[str, Any]:
    """Fetch live cryptocurrency prices and 24h market trends from CoinGecko."""
    if not coins:
        coins = ["BTC", "ETH", "SOL", "TON", "DOGE"]

    selected_ids = []
    for c in coins:
        c_up = c.upper()
        if c_up in CRYPTO_ID_MAP:
            selected_ids.append(CRYPTO_ID_MAP[c_up][0])
        else:
            selected_ids.append(c.lower())

    ids_param = ",".join(selected_ids)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_param}&vs_currencies=usd,inr&include_24hr_change=true"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)

        if resp.status_code != 200:
            return {"success": False, "error": "Crypto price service temporarily unavailable."}

        data = resp.json()
        results = []

        for symbol, (coin_id, label, icon) in CRYPTO_ID_MAP.items():
            if coin_id in data:
                c_data = data[coin_id]
                usd_price = c_data.get("usd", 0)
                inr_price = c_data.get("inr", 0)
                usd_24h = c_data.get("usd_24h_change", 0) or 0

                change_icon = "🟢" if usd_24h >= 0 else "🔴"
                results.append({
                    "symbol": symbol,
                    "label": label,
                    "icon": icon,
                    "usd": f"${usd_price:,.2f}" if usd_price >= 1 else f"${usd_price:,.4f}",
                    "inr": f"₹{inr_price:,.2f}" if inr_price >= 1 else f"₹{inr_price:,.4f}",
                    "change": f"{change_icon} {usd_24h:+.2f}%",
                })

        return {"success": True, "data": results}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def convert_currency(amount: float, from_curr: str, to_curr: str) -> Dict[str, Any]:
    """Calculate real-time currency exchange rates."""
    from_c = from_curr.strip().upper()
    to_c = to_curr.strip().upper()

    url = f"https://open.er-api.com/v6/latest/{from_c}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)

        data = resp.json()
        if data.get("result") != "success":
            return {"success": False, "error": f"Unsupported base currency '{from_c}'."}

        rates = data.get("rates", {})
        if to_c not in rates:
            return {"success": False, "error": f"Target currency '{to_c}' not found."}

        rate = rates[to_c]
        converted = amount * rate
        last_updated = data.get("time_last_update_utc", "Recent")

        return {
            "success": True,
            "amount": amount,
            "from": from_c,
            "to": to_c,
            "rate": rate,
            "converted": converted,
            "formatted_result": f"{amount:,.2f} {from_c} = {converted:,.2f} {to_c}",
            "updated_at": last_updated,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
